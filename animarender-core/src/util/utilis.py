
from models.profits import Profits

def get_new_jobs_ids(jobs, profits):

	# getting ids of jobs for which
	# costs where not calculated yet
	# returns list of ids
    
    jobs_list = [job.dict for job in jobs]
    profits_list = [profit.dict for profit in profits]
    jobs_list_ids = [job['id'] for job in jobs_list]
    profits_list_ids = [profit['id'] for profit in profits_list]
    s = set(profits_list_ids)
    return [ID for ID in jobs_list_ids if ID not in s]

def json_into_modelObject(json):

	# returns list of modelObjects
	
	i = 0;
	modelObjects = []
	while (i < len(json)):
		modelObjects.append(Profits(**json[i]))
		i += 1
	return modelObjects