
import numpy as np
import matplotlib.pyplot as plt
import scipy.special as ss
from matplotlib import animation

#TRIDIAGONAL ALGORITHM
def tridiag(a, b, c, d):
    """
    Analogous to the function tridiag.f
    Refer to http://en.wikipedia.org/wiki/Tridiagonal_matrix_algorithm
    """
    n = len(a)

    cp = np.zeros(n, dtype = np.complex)
    dp = np.zeros(n, dtype = np.complex)
    cp[0] = c[0]/b[0]
    dp[0] = d[0]/b[0]

    for i in range(1,n):
        m = (b[i]-a[i]*cp[i-1])
        cp[i] = c[i]/m
        dp[i] = (d[i] - a[i]*dp[i-1])/m

    x = np.zeros(n, dtype = np.complex)
    x[n-1] = dp[n-1]

    for j in range(1,n):
        i = (n-1)-j
        x[i] = dp[i]-cp[i]*x[i+1]

    return x

#CRANK-NICOLSON
def CrankNicolson (dx,dt,ndim,ntime,r,V,psi):
    
    #A sup and inf diagonals
    A1=np.full(ndim,-r,dtype=complex)
    A3=np.full(ndim,-r,dtype=complex)
    
    A1[ndim-1]=0.
    A3[0]=0.
    
    #B matrix
    B=np.zeros((ndim,ndim),dtype=complex)
    for i in range(0,ndim):
        for j in range(0,ndim):
            if i==j:
                x=i*dx
                y=j*dx
                B[i,j]=1.-2.*r-1j*dt*V(x,y)/(4.*hbar)
            if i==j+1 or i+1==j:
                B[i,j]=r
    
    norma=[]
    for t in range(0,ntime+1):
        
        psi=CrankStep(dx,dt,ndim,r,V,psi,A1,A3,B)
        
        prob=Probability(psi,ndim)
        print(Norm(prob,ndim,dx), t)
        norma=np.append(norma,Norm(prob,ndim,dx))
    
    return psi,norma

def CrankStep (dx,dt,ndim,r,V,psi,Asup,Ainf,Bmatrix):    
    "1 timestep evolution"
            
    "Evolve for x"
    for j in range(0,ndim):
        
        #Adiag
        Adiag=[]
        for i in range(0,ndim):
            x=i*dx
            y=j*dx
            Adiag=np.append(Adiag,(1.+2.*r+1j*dt*V(x,y)/(4.*hbar)))
        #Psix
        psix=[]
        for i in range(0,ndim):
            psix=np.append(psix,psi[i,j])
        #Bmatrix*Psi0 
        Bproduct=np.dot(Bmatrix,psix)
        
        #Tridiagonal
        psix=tridiag(Ainf,Adiag,Asup,Bproduct)
        
        #Change the old for the new values of psi
        for i in range(0,ndim):
            psi[i,j]=psix[i]
            
    "Evolve for y"
    for i in range(0,ndim):
        
        #Adiag
        Adiag=[]
        for j in range(0,ndim):
            x=i*dx
            y=j*dx
            Adiag=np.append(Adiag,(1.+2.*r+1j*dt*V(x,y)/(4.*hbar)))
        #Psix
        psiy=[]
        for j in range(0,ndim):
            psiy=np.append(psiy,psi[i,j])
        #Bmatrix*Psi 
        Bproduct=np.dot(Bmatrix,psiy)
        #Tridiagonal
        psiy=tridiag(Ainf,Adiag,Asup,Bproduct)
        
        #Change the old for the new values of psi
        for j in range(0,ndim):
            psi[i,j]=psiy[j]
            
    return psi

#POTENTIAL
def Pot(x,y):
    k=1.
    x0=ndim*dx/2.
    return 0.5*k*((x-x0)**2+(y-x0)**2)

#INITIAL FUNCTION
        #x->a
        #y->b
def EigenOsci(x,y,a,b):
    k=1.
    m=1.
    w=np.sqrt(k/m)
    zetx=np.sqrt(m*w/hbar)*(x-2.5)
    zety=np.sqrt(m*w/hbar)*(y-2.5)
    Hx=ss.eval_hermite(a,zetx)
    Hy=ss.eval_hermite(b,zety)
    c_ab=(2**(a+b)*np.math.factorial(a)*np.math.factorial(b)*np.pi)**(-0.5)
    return c_ab*np.exp(-0.5*(zetx**2+zety**2))*Hx*Hy

def Coherent(x,y,x0,y0):
    k=1.
    m=1.
    w=np.sqrt(k/m)
    
#    a=b=0.
    xx=x-x0
    yy=y-y0
    
    c=(m*w/(np.pi*hbar))**0.5
    e1=1.
    e2=1.  #np.exp(np.sqrt(2*m*w/hbar)*(a*xx+b*yy))
    e3=np.exp(-0.5*(m*w/hbar)*(xx**2+yy**2))
    return c**2*e1*e2*e3

#PROBABILITY
def Probability(f,n):
    p=np.zeros((n,n),dtype=float)
    for i in range (0,n):
        for j in range (0,n):
            p[i,j]=np.real(np.conjugate(f[i,j])*f[i,j])
    return p

#MATRIX OF POTENTIAL
def Potential_matrix(V,dim):
    pot=np.zeros((dim,dim),dtype=float)
    for i in range (0,dim):
        for j in range (0,dim):
            x=dx*i
            y=dx*j
            pot[i,j]=V(x,y)
    return pot

#NORM
def Norm(probab,dim,pas):
    norm=0.
    for i in range (0,dim):
        for j in range (0,dim):
            norm=norm+probab[i,j]
    return norm*pas**2
    



#FIGURE SHOWING POTENTIAL, NORM EVOLUTION AND INTIAL+FINAL PROBABILITY
def fig(Fu0,V,ndim,ntime,a,b):
        #Potential matrix
    po=Potential_matrix(V,ndim)
        
        #Initial psi
    psi0=np.zeros((ndim,ndim),dtype=complex)
    for i in range (0,ndim):
        for j in range (0,ndim):
            x=dx*i
            y=dx*j
            psi0[i,j]=Fu0(x,y,a,b)
    Ppsi0=Probability(psi0,ndim)
    
        #Final psi
    psi,norma=CrankNicolson(dx,dt,ndim,ntime,r,V,psi0)
    Ppsi=Probability(psi,ndim)
    
        #Print norms        
    print('Norm ini t')
    print(Norm(Ppsi0,ndim,dx))
    print('Norm final t')
    print(Norm(Ppsi,ndim,dx))
    
        #Figures
    plt.figure()
            #Potential (colormap)
    plt.subplot(2,2,1)
    plt.title('Potential')
    plt.imshow(po,cmap="plasma")
            #Initial psi
    plt.subplot(2,2,2)
    plt.title('Initial')
    plt.imshow(Ppsi0,cmap="plasma")
    plt.axis('off')
            #Final psi
    plt.subplot(2,2,4)
    plt.title('Final')
    plt.imshow(Ppsi,cmap="plasma")
    plt.axis('off')
            #Norm evolution
    plt.subplot(2,2,3)
    plt.title('Evol norma')
    plt.plot(norma)
    
    plt.show()
    return


#GIF OF TIME EVOLUTION
def anim(Fu0,V,ndim,ntime,a,b):
    
    fig = plt.figure()
    
    #Initial Psi
    psi=np.zeros((ndim,ndim),dtype=complex)
    for i in range (0,ndim):
        for j in range (0,ndim):
            x=dx*i
            y=dx*j
            psi[i,j]=Fu0(x,y,a,b)
    print(Norm(Probability(psi,ndim),ndim,dx))
    #A sup and inf diagonals
    A1=np.full(ndim,-r,dtype=complex)
    A3=np.full(ndim,-r,dtype=complex)
    
    A1[ndim-1]=0.
    A3[0]=0.
    
    #B matrix
    B=np.zeros((ndim,ndim),dtype=complex)
    for i in range(0,ndim):
        for j in range(0,ndim):
            if i==j:
                x=i*dx
                y=j*dx
                B[i,j]=1.-2.*r-1j*dt*V(x,y)/(4.*hbar)
            if i==j+1 or i+1==j:
                B[i,j]=r
    #Animation
    ims = []
    for i in range(ntime):
        psi=CrankStep(dx,dt,ndim,r,V,psi,A1,A3,B)
        im = plt.imshow(Probability(psi,ndim), animated=True)
        ims.append([im])
    
    ani=animation.ArtistAnimation(fig,ims,interval=50,blit=True,repeat_delay=500)
    print(Norm(Probability(psi,ndim),ndim,dx))
#    ani.save('TEvol.gif')
    ani.show()
    return
    
#############################################################################

ndim=n=100
#ntime=100

dx=0.05
dt=0.01

m=1.
hbar=1.
r=1j*dt/(4.*m*dx**2)


f=fig(EigenOsci,Pot,ndim=100,ntime=100,a=0,b=0)
#an=anim(EigenOsci,Pot,ndim,ntime=100,a=0,b=0)

#f=fig(Coherent,Pot,ndim=100,ntime=100,a=1.,b=2.5)
#an=anim(Coherent,Pot,ndim,ntime=200,a=2.,b=2.5)