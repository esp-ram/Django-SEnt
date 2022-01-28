# Importing packages
import matplotlib.pyplot as plt
import numpy as np

# Creating a sample data for x-values
x = np.arange(2, 40000, 4)

variable = (104.33/1000*x)
fijo = (0*x) + 1140000/1000
varmasfijo = (104.33/1000*x)+ 1140000/1000
ventas = (150/1000*x)

# Plotting the line created by the linear function
plt.plot(x, variable, 'c', linewidth=2, label='C. Variable')
plt.plot(x, fijo, 'b', linewidth=2, label='C. Fijo')
plt.plot(x, varmasfijo, 'g', linewidth=2, label='CF + CV')
plt.plot(x, ventas, 'r', linewidth=2, label='I. Ventas')

plt.title('Diagrama de Knoppel')
plt.xlabel('Litros producidos')
plt.ylabel('Miles de Pesos')
plt.legend()
plt.show()
