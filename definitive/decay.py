'''
This code simulates concentration decay 
for a range a decay constants.
If you forget what it means have a look at
https://en.wikipedia.org/wiki/Exponential_decay#Solution_of_the_differential_equation
'''

import matplotlib.pyplot as plt

c= []
c0= 1
e= 2.718281828459045
ln2= 0.69314
lmb= [1/25,1/5,1]
time_span= 7 
t= [x/10 for x in range(time_span*10)]
colors=['r','g','b']

fig= plt.figure('Exponential decay for a range of decay constants',figsize=(10,7))
ax= fig.add_subplot(111)
#ax.set_yscale('log')
ax.grid(alpha= 0.5)

for l in range(len(lmb)):

	for tt in t:
		c.append(  c0 * e**(-lmb[l]*tt) )
	
	ax.plot(c, color= colors[l], 
         label= '{:.2f} min⁻1; tau {:.1f}min; t1/2 {:.1f}min'.format(lmb[l],1/lmb[l], ln2/lmb[l])
         )
	c= []

ax.hlines(y= c0/e, xmin= -1, xmax= t[-1]*10, ls= ':', alpha= 0.3)
ax.text(x= -3, y= c0/e, s= '1/e', fontsize= 10)
ax.set_xticks(range(0,len(t)+10,10))
ax.set_xticklabels(range(0,time_span+1))
ax.set_xlabel('Minutes')
ax.set_ylabel('Arbitray units')
ax.text(x= 40, y= 0.6, s= r'$K_{el}\ =\ \frac{1}{\tau}\ =\ \frac{Ln(2)}{t_{1/2}}$', fontsize= 24, alpha= 0.5)
ax.legend()

plt.show()

