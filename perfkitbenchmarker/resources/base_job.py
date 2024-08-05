"""Base class for representing a job / instance."""

import threading
from typing import List, Type, TypeVar
from absl import flags
from perfkitbenchmarker import resource
from perfkitbenchmarker import sample
from perfkitbenchmarker.resources import jobs_setter

FLAGS = flags.FLAGS


class BaseJob(resource.BaseResource):
  """Base class for representing a cloud job / instance.

  Handles lifecycle management (creation & deletion) for a given Cloud Run Job.

  Attributes:
    RESOURCE_TYPE: The class name.
    REQUIRED_ATTRS: Required field for subclass to override (one constant per
      subclass).
    region: Region the job should be in.
    backend: Amount of memory allocated.
    samples: Samples with lifecycle metrics (e.g. create time) recorded.
  """

  RESOURCE_TYPE: str = 'BaseJob'
  REQUIRED_ATTRS: List[str] = ['SERVICE']
  SERVICE: str
  _POLL_INTERVAL: int = 1
  _job_counter: int = 0
  _job_counter_lock: threading.Lock = threading.Lock()

  def __init__(self, base_job_spec: jobs_setter.BaseJobSpec):
    super().__init__()
    self.name: str = self._GenerateName()
    self.region: str = base_job_spec.job_region
    self.backend: str = base_job_spec.job_backend
    # update metadata
    self.metadata.update({
        'backend': self.backend,
        'region': self.region,
        # 'concurrency': 'default',
    })
    self.samples: List[sample.Sample] = []

  def _GenerateName(self) -> str:
    """Generates a unique name for the job.

    Locking the counter variable allows for each created job name to be
    unique within the python process.

    Returns:
      The newly generated name.
    """
    with self._job_counter_lock:
      self.job_number: int = self._job_counter
      name: str = f'pkb-{FLAGS.run_uri}'
      name += f'-{self.job_number}'
      BaseJob._job_counter += 1
      return name

  def Execute(self):
    """Executes the job."""
    pass


JobChild = TypeVar('JobChild', bound='BaseJob')


def GetJobClass(service: str) -> Type[JobChild] | None:
  """Returns class of the given Job type.

  Args:
    service: String which matches an inherited BaseJob's required SERVICE value.
  """
  return resource.GetResourceClass(BaseJob, SERVICE=service)