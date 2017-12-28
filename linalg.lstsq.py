## linear regression
A = np.vstack( [e123, np.ones(len(e123))] ).T
m,c = np.linalg.lstsq(A,edirect)[0]
print m,c

## plot
plt.figure(figsize = (8,8))

x = np.linspace(-25,10,1000)
y = m*x+c
plt.plot(x,y,color = 'green',label="y = %g*x+%g"%(m,c) ,linewidth=2)
