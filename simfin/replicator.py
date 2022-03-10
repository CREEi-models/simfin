from simfin import simulator
from copy import deepcopy
from multiprocessing import Pool as pool
from multiprocessing import cpu_count
import psutil
import ray

@ray.remote
def run_model(m):
	m.simulate()
	return m

class replicator:
	def __init__(self,nreps,ncpus):
		self.nreps = nreps
		self.ncpus = ncpus
	def set_model(self,model):
		self.models = []
		for m in range(self.nreps):
			self.models.append(deepcopy(model))

	def replicate(self):
		if self.ncpus>1:
			ray.shutdown()
			ray.init(num_cpus=self.ncpus,ignore_reinit_error=True)
			self.models = ray.get([run_model.remote(m) for m in self.models])
		else :
			self.models = [run_model.remote(m) for m in self.models]
		return

