from model.db.DGJobAccess import DGJobAccess

def testJobAccess():
    access = DGJobAccess()
    # jobData = {
    #   'JobType': 'MMSE',
    #   'JobStatus': 'PENDING',
    #   'JobOwner': 'test@test.com'
    # }
    # id, stat = access.insertJob(jobData)
    # print(id , stat)

    # jobData = {
    #   'JobStartDate': datetime.now()
    # }
    # cnt, stat = access.updateJobById(jobData, 1)
    # print(cnt , stat)

    # cnt, stat = access.deleteJobById( 1)
    # print(cnt , stat)
    # job = access.getMostRecentJobForUser('test@test.com', ['PENDING','APPLIED'])
    # print(job)
    jobs = access.getJobsForUser('test@test.com')
    for job in jobs:
        print(job)
# testJobAccess()