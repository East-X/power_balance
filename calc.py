import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import norm
from math import sqrt
from math import pi
from math import exp
from scipy.stats import laplace
        
un = 110
ur = 110
xc = 10
eq = 110
xd_asterisk = 1
eq_asterisk = 110
xd = 3
koef_power_after_fault = 1/3
omega_delta = 2.5 * np.pi
time_protection_on = 0.03 #sec
delta_step = 1

x = np.arange(0, 180, delta_step)
p_normal = eq*un/(xc+xd)*np.sin(x*np.pi/180) # no Automatic excitation control
#p_normal = eq_asterisk*un/(xc+xd_asterisk)*np.sin(x*np.pi/180) # Automatic regulation of constant excitation
#p_normal = ur*un/(xc+0)*np.sin(x*np.pi/180) # Automatic regulation of strong excitation

p_fault = p_normal * koef_power_after_fault
p_after_fault = eq_asterisk*un/(2 * xc+xd)*np.sin(x*np.pi/180)

p_turbine = list()
  
p_turbine_value = np.max(p_normal) / 2 # halve from peak
p_turbine = np.empty(len(x))
p_turbine.fill(p_turbine_value)

p_normal_turbine_delta = np.array_split(np.abs(p_normal - p_turbine_value), 2)
p_after_fault_turbine_delta = np.array_split(np.abs(p_after_fault - p_turbine_value), 2)

p_normal_turbine_delta_a = p_normal_turbine_delta[0]
p_after_fault_turbine_delta_a = p_after_fault_turbine_delta[0]

min_p_normal_turbine_delta_a = np.min(p_normal_turbine_delta_a)
min_p_after_fault_turbine_delta_a = np.min(p_after_fault_turbine_delta_a)

x_equilibrium_a = 0
idx_a = 0
idx_protection = 0
idx_e = 0

for idx in range(len(p_normal_turbine_delta_a)):
   value = p_normal_turbine_delta_a[idx]
   if value == min_p_normal_turbine_delta_a:
       idx_a = idx
       x_equilibrium_a = x[idx]
       break

x_protection_on = x_equilibrium_a + omega_delta*180/np.pi*time_protection_on

for idx in range(len(x)):
   value = x[idx]
   if value >= x_protection_on:
       idx_4 = idx
       break

for idx in range(len(p_after_fault_turbine_delta_a)):
   value = p_after_fault_turbine_delta_a[idx]
   if value == min_p_after_fault_turbine_delta_a:
       idx_e = idx
       break

print(f'x_equilibrium_a is {x_equilibrium_a}')
print(f'x_protection_on is {x_protection_on}')

p_fault_extracted = np.array(p_fault[idx_a:idx_4])
p_turbine_extracted = np.array(p_turbine[idx_a:idx_4])

area_acceleration = round(np.trapz(p_turbine_extracted)-np.trapz(p_fault_extracted), 2)

p_after_fault_extracted = np.array(p_after_fault[idx_e:len(p_after_fault_turbine_delta_a)])
p_turbine_extracted = np.array(p_turbine[idx_e:len(p_after_fault_turbine_delta_a)])

area_deceleration = round(np.trapz(p_after_fault_extracted)-np.trapz(p_turbine_extracted), 2)
area_deceleration = area_deceleration * 2 # as we count halve of fill

koef_stability = round(area_deceleration/area_acceleration, 2)

print(f'area acceleration is {area_acceleration}')
print(f'area deceleration is {area_deceleration}')
print(f'Dynamic stability safety factor initial: {koef_stability}')

fig, ax = plt.subplots()
ax.plot(x, p_normal)
ax.plot(x, p_fault)
ax.plot(x, p_turbine)
ax.plot(x, p_after_fault)

ax.set(xlabel='delta', ylabel='power', title='Angular characteristics of power transmission during a short circuit')
ax.grid()

ax.fill_between(x ,p_after_fault, p_turbine, where = (p_after_fault>p_turbine), color = 'green', alpha=0.5)
ax.fill_between(x ,p_fault, p_turbine, where = (x > x_equilibrium_a) & (x < x_protection_on), color = 'red', alpha=0.5)

p_turbine_init = p_turbine_value

while (koef_stability < 1) & (p_turbine_value > 0.0):
    p_turbine_value = p_turbine_value - 5.0  
    p_turbine.fill(p_turbine_value)
    p_after_fault_turbine_delta = np.array_split(np.abs(p_after_fault - p_turbine_value), 2)
    p_after_fault_turbine_delta_a = p_after_fault_turbine_delta[0]
    min_p_after_fault_turbine_delta_a = np.min(p_after_fault_turbine_delta_a)
    for idx in range(len(p_after_fault_turbine_delta_a)):
       value = p_after_fault_turbine_delta_a[idx]
       if value == min_p_after_fault_turbine_delta_a:
           idx_e = idx
           break

    p_after_fault_extracted = np.array(p_after_fault[idx_e:len(p_after_fault_turbine_delta_a)])
    p_turbine_extracted = np.array(p_turbine[idx_e:len(p_after_fault_turbine_delta_a)])

    area_deceleration = round(np.trapz(p_after_fault_extracted)-np.trapz(p_turbine_extracted), 2)
    area_deceleration = area_deceleration * 2 # as we count halve of fill
    koef_stability = round(area_deceleration/area_acceleration, 2)  

print(f'Dynamic stability safety factor after power reduction: {koef_stability}')
print(f'Reduce power : {round(p_turbine_init,2)} -> {round(p_turbine_value,2)}')

ax.plot(x, p_turbine)
ax.legend (('normal', 'fault', 'turbine 1', 'after fault', 'S deceleration', 'S acceleration', 'turbine 2'))
    
fig.savefig("power_curve.png")
plt.show()