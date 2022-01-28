from smtplib import SMTPException
from django.shortcuts import get_object_or_404,render
from django.forms import formset_factory
from django.core.exceptions import ObjectDoesNotExist
from .models import Professor, Exam, Student
from django.utils import timezone
from deta import Deta
import datetime, time, os, base64, random, tempfile, zipfile
from django.urls import reverse
from django.http import Http404, HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from decimal import Decimal, ROUND_HALF_UP, ROUND_UP
from django.core.mail import EmailMessage
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from .forms import EntregaFormSetHelper, MyEntregaForm, BaseEntregaFormSet
import json
from dotenv import load_dotenv
load_dotenv()

DETA = Deta(os.getenv('DETA_SECRET'))
AES_SIZE = int(os.getenv('AES_KEY_SIZE'))
DB = DETA.Base(os.getenv('DETA_DB_NAME'))
AES_KEY =base64.b64decode(os.getenv('AES_KEY'))


def iso_date():
    todays_Date = datetime.date.fromtimestamp(time.time())
    return(todays_Date.isoformat())


def handle_uploaded_file_cyph(file,name,drive_name):

    drive = DETA.Drive(drive_name)
    aes_mode_key = os.urandom(AES_SIZE)
    e_data = base64.b64encode(file.read())
    
    #length of data must be a multiple of the AES key size
    length = len(e_data)
    size_round_up = Decimal(length/AES_SIZE).quantize(Decimal('1'), rounding=ROUND_UP)
    bytes_needed = ((int(size_round_up)*AES_SIZE)-(length))
    e_data += b'='*(bytes_needed)


    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(aes_mode_key))
    encryptor = cipher.encryptor()
    ct = encryptor.update(e_data) + encryptor.finalize()

    try:
        drive.put(name, ct)
    except Exception as e:
        return None
    return aes_mode_key


def home(request):
    context = {}
    examenes = Exam.objects.filter(end__gt = timezone.now(), start__lt = timezone.now())
    proximos = Exam.objects.filter(start__gt= timezone.now())
    context["active"] = examenes
    context["upcoming"] = proximos

    return render(request, 'home.html', context)



def new_submit(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)


    if not exam.is_active(timezone.now()):
        raise Http404

    ArticleFormSet = formset_factory(MyEntregaForm, formset=BaseEntregaFormSet)
    context = {}
    formset = ArticleFormSet(form_kwargs={'exercises': exam.exercises})


    if request.method == 'POST':
        formset = ArticleFormSet(request.POST, request.FILES,form_kwargs={'exercises': exam.exercises})
        
        if formset.is_valid():
            data = formset.cleaned_data[0]
            if not data:
                return HttpResponseRedirect(reverse('examen:submit_fail'))

            name,student_id = data.pop('name').replace(' ',''),data.pop('student_id')
            db_data = DB.put({'name':name,'student_id':student_id,'exam':exam.title,'date':iso_date()})
            db_key = db_data['key']

            Success = True
            valid_ex = 0

            for key in data:
                if data[key] != None and Success:
                    filename = data[key].name.split('.')[1]
                    string = f"{name}-{student_id}-{key.replace(' ','')}.{filename}"
                    aes_iv = handle_uploaded_file_cyph(data[key],string,exam.db_safe_title())
                    if aes_iv == None:
                        Success = False
                    else:
                        DB.update({f"{key.replace(' ','')}":string, f"{key.replace(' ','')}_aes":(base64.b64encode(aes_iv)).decode("utf-8")},db_key)
                        valid_ex += 1
            
            if Success:
                try:
                    new_submit = Student.objects.get(student_id = student_id, examen_id = exam)
                except ObjectDoesNotExist:
                    new_submit = Student()
                    new_submit.student_id = student_id
                    new_submit.name = name
                    new_submit.exam = exam
                
                new_submit.data_key = db_key
                new_submit.ex_submitted = valid_ex
                new_submit.save()


                student_b64 = (base64.b64encode(bytes(str(new_submit.id), 'utf-8')))

                return HttpResponseRedirect(reverse('examen:submit_success', kwargs={'student_id' : student_b64.decode("utf-8")}))
            
            return HttpResponseRedirect(reverse('examen:submit_fail'))

    helper = EntregaFormSetHelper()

    context['formset'] = formset
    context['helper'] = helper
    context['exam'] = exam


    return render(request, 'new_submit.html', context)


def submit_success(request,student_id_b64):
    student_pk = (base64.b64decode(student_id_b64)).decode("utf-8")
    student = get_object_or_404(Student, pk = student_pk)


    return render(request,'submit_success.html',{'id':student.data_key})


def submit_fail(request):
    return render(request,'submit_fail.html')



@staff_member_required(redirect_field_name='',login_url='examen:home')
def assignation(request,exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    if exam.report != 'N/A':
        raise Http404
    students = Student.objects.filter(exam_id = exam)
    professors = Professor.objects.filter(available = True)

    key_list = []
    
    for student in students:
        db_key = student.data_key
        key_list.append(db_key)

    db_data = DB.put({'exam':exam.title,'date':iso_date()})
    db_key = db_data['key']
    
    professors = list(professors)
    random.shuffle(professors)
    students = list(students)
    professors_num = len(professors)
    students_num = len(students)
    alloc = Decimal(students_num/professors_num).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    
    while professors and students:
        choice_professor = professors[0]
        professors.remove(choice_professor)
        
        if professors:
            assigned_students = random.sample(students,k=int(alloc))
        
        else:
            assigned_students = students

        if assigned_students:
            DB.update({choice_professor.id : {x.name:x.data_key for x in assigned_students}},db_key)
        
            for x in assigned_students:
                students.remove(x)
        

    setattr(exam,'report',db_key)
    exam.save()


    return HttpResponseRedirect(reverse('examen:report', kwargs={'exam_id' : exam_id}))



@staff_member_required(redirect_field_name='',login_url='examen:home')
def exam_report(request,exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)

    raw_data = DB.get(exam.report)
    students = Student.objects.filter(exam_id = exam)
    key_list = []
    
    for student in students:
        db_key = student.data_key
        key_list.append(db_key)


    exam_name = raw_data.pop('exam')
    date = raw_data.pop('date')
    key = raw_data.pop('key')

    aux_dict = {}

    for k,v in raw_data.items():
        professor = Professor.objects.get(id = k)
        aux_dict[professor] = v


    script_data = {"base_name": (DB.base_path).split('/')[-1],
                "drive_name": exam.db_safe_title(),
                "key_list" : key_list,
                "exercises" : exam.exercises,
                "key" : key}
    script_data = json.JSONEncoder().encode(script_data)

    return render(request,'report.html',{'data':aux_dict, 'exam_id':exam_id,'exam':exam_name,'date':date,'key':key,'script_data':script_data})


def live_submit(request):
    context = {}
    exams = Exam.objects.filter(end__gt = timezone.now(), start__lt = timezone.now())
    for exam in exams:
        context[exam.title] = Student.objects.filter(exam_id = exam)
    return render(request, 'live_submit.html', {'data':context})


def zip_sender(students, corrector, exam):
    body_text = 'Students:\n'
    drive = DETA.Drive(exam.db_safe_title())
    with tempfile.NamedTemporaryFile(suffix = '.zip', prefix=f'submits-{exam.titulo}-') as outerfile:
        with zipfile.ZipFile(outerfile, 'w', zipfile.ZIP_DEFLATED) as outerzip:

            for student, data_key in students.items():
                info = DB.get(data_key)
                
                with tempfile.NamedTemporaryFile() as tmp:
                    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as archive:
                        
                        for num in range(exam.exercises):
                            try:
                                a = tempfile.NamedTemporaryFile()
                                dwnfile=drive.get(info[f'ex{num}'])
                                
                                aes_mode_key_64 = info[f'ex{num}_aes']
                                aes_mode_key = base64.b64decode(aes_mode_key_64)
            
                                cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(aes_mode_key))
                                decryptor = cipher.decryptor()
                                e_data = decryptor.update(dwnfile.read()) + decryptor.finalize()
                                data = base64.b64decode(e_data)
                                
                                a.write(data)
                                a.seek(0)
                                
                                archive.write(a.name, arcname = info[f'ex{num}'])
                            except:
                                pass
                            
                        tmp.seek(0)
                    outerzip.write(tmp.name, arcname = f'zip-{student}.zip')
                    body_text += f'{info["name"]} - {info["student_id"]}\n'
        outerfile.seek(0)
    
        email = EmailMessage(
            subject=f'You have exams to grade from {exam.title}',
            body=body_text,
            to=[corrector.email],
            cc=[''])
        email.attach_file(outerfile.name,'application/zip')
        email.send()



@staff_member_required(redirect_field_name='',login_url='examen:home')
def sender(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    raw_data = DB.get(exam.reporte)
    data_for_email = []
    professor_name = ""

    if 'corrector' in request.GET.keys():
        try:
            submits = raw_data[request.GET['professor']]
            professor = Professor.objects.get(id = request.GET['professor'])
            professor_name = professor.name
            data_for_email.append((professor,submits))
        except KeyError as e:
            print("there is no professor named: ", e)
    else:
        raw_data.pop('date')
        raw_data.pop('exam')
        raw_data.pop('key')
        professor_name = "everyone"
        for k,v in raw_data.items():
            professor = Professor.objects.get(id = k)
            submits = v
            data_for_email.append((professor,submits))
    

    for item in data_for_email:
        try:
            zip_sender(item[1],item[0],exam)
        except SMTPException as email_exc:
            return HttpResponseRedirect(reverse('examen:reporte', kwargs={'exam_id' : exam_id})+"?failed")


    return HttpResponseRedirect(reverse('examen:reporte', kwargs={'exam_id' : exam_id})+f"?sentto={professor_name}")
    