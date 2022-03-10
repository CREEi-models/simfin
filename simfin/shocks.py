import numpy as np
import pandas as pd

class shocks:
    def __init__(self,alpha,Phi,V,stochastic):
        self.alpha = alpha.to_numpy()
        self.Phi = Phi.to_numpy()
        self.V = V.to_numpy()
        self.outcomes = Phi.columns.to_list()
        self.J = len(self.outcomes)
        if stochastic:
            self.L = np.linalg.cholesky(self.V)
        else :
            self.L = np.zeros((self.J,self.J))
        self.nq = 4
        return
    def start_from(self,last_shocks):
        self.state = last_shocks
    def update_one_q(self,q):
        state = self.state.to_numpy().reshape((self.J,1))

        eps = np.random.normal(size=self.J).reshape((self.J,1))
        next_state = self.alpha[:,q-1].reshape((self.J,1)) + self.Phi @ state\
                     + self.L @ eps
        self.state = pd.Series(index = self.state.index, data = next_state[:,0])
        return
    def update_1yr(self):
        register = pd.DataFrame(index=self.state.index,columns = [x for x in
                                                                  range(1,5)])
        for q in range(1,5):
            self.update_one_q(q)
            register.loc[:,q] = self.state.to_list()
        return register

