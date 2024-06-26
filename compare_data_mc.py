import matplotlib.pyplot as plt
import numpy as np

# Dati forniti
data = np.array([0.00000e+00, 1.63200e+03, 1.56500e+03, 1.10600e+03, 1.01600e+03, 1.09300e+03,
                  1.30900e+03, 1.70500e+03, 2.49600e+03, 3.58200e+03, 5.80500e+03, 9.35600e+03,
                  1.41700e+04, 2.15300e+04, 3.15380e+04, 4.38260e+04, 5.90250e+04, 7.78690e+04,
                  1.00291e+05, 1.24806e+05, 1.52637e+05, 1.82857e+05, 2.13304e+05, 2.45650e+05,
                  2.75639e+05, 3.07365e+05, 3.38031e+05, 3.66938e+05, 3.93979e+05, 4.19661e+05,
                  4.42014e+05, 4.67232e+05, 4.85711e+05, 5.05815e+05, 5.22500e+05, 5.37665e+05,
                  5.49403e+05, 5.56152e+05, 5.59300e+05, 5.56296e+05, 5.48060e+05, 5.36144e+05,
                  5.15351e+05, 4.93804e+05, 4.67435e+05, 4.33933e+05, 4.00814e+05, 3.65605e+05,
                  3.27752e+05, 2.92519e+05, 2.57433e+05, 2.25040e+05, 1.93633e+05, 1.65007e+05,
                  1.38877e+05, 1.16847e+05, 9.65410e+04, 7.97520e+04, 6.50830e+04, 5.27640e+04,
                  4.25030e+04, 3.44150e+04, 2.71880e+04, 2.15190e+04, 1.75630e+04, 1.35900e+04,
                  1.09770e+04, 8.39000e+03, 6.56400e+03, 5.13200e+03, 3.89000e+03, 3.11800e+03,
                  2.36700e+03, 1.93100e+03, 1.51100e+03, 1.23700e+03, 8.77000e+02, 6.83000e+02,
                  5.41000e+02, 4.27000e+02, 3.21000e+02, 2.77000e+02, 2.19000e+02, 1.67000e+02,
                  1.34000e+02, 1.02000e+02, 7.50000e+01, 6.70000e+01, 4.20000e+01, 3.40000e+01,
                  3.60000e+01, 2.20000e+01, 4.60000e+01, 1.00000e+01, 1.30000e+01, 1.30000e+01,
                  1.20000e+01, 1.70000e+01, 4.00000e+00, 7.00000e+00])

mc = np.array([0.0, 1632.0, 1565.0, 1106.0, 1016.0, 1093.0, 1309.0, 1704.9999, 2496.0, 3582.0,
                  5805.0, 9356.0, 14170.0, 21530.0, 31538.0, 43826.0, 59025.0, 77869.0, 100291.0,
                  124806.01, 152637.0, 182857.0, 213304.0, 245650.0, 275639.0, 307365.0, 338031.0,
                  366938.0, 393979.0, 419661.0, 442014.0, 467232.0, 485711.0, 505815.0, 522500.0,
                  537665.0, 549403.0, 556152.0, 559300.0, 556296.0, 548060.0, 536144.0, 515351.0,
                  493803.97, 467435.03, 433933.0, 400814.0, 365605.0, 327752.0, 292519.0, 257433.0,
                  225040.0, 193633.0, 165007.0, 138877.0, 116847.0, 96541.0, 79752.0, 65083.0,
                  52764.0, 42503.0, 34415.0, 27188.0, 21519.0, 17563.0, 13590.0, 10977.0, 8390.0,
                  6564.0, 5132.0, 3889.9998, 3118.0, 2367.0, 1931.0001, 1510.9999, 1237.0, 877.0,
                  683.0, 541.0, 427.0, 321.0, 277.0, 219.0, 167.0, 134.0, 102.0, 75.0, 67.0,
                  42.0, 34.0, 0.0, 22.0, 46.0, 10.0, 0.0, 0.0, 0.0, 17.0, 0.0, 0.0])


plt.figure(figsize=(10, 6))

# Plot dei dati1 come barre
plt.bar(range(len(mc)), mc, label='mc', color='blue', alpha=0.7)
plt.scatter(range(len(data)), data, color='orange', marker='o', label='data')

# Personalizzazione del grafico
plt.title('N Vertices distribution')
plt.xlabel('N Vertices')
plt.ylabel('entries')
plt.legend()
plt.grid(True)

# Mostra il grafico
plt.show()