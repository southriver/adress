from datetime import  datetime
import mysql
from model.db.RecordAccess import RecordAccess


class DGJobAccess(RecordAccess):

    SQL_INSERT = ("INSERT INTO DGJob "
              "(JobType, JobOwner, JobData, JobStatus, JobResult, JobCreateDate, JobStartDate, JobEndDate) "
              "VALUES (%(JobType)s, %(JobOwner)s, %(JobData)s, %(JobStatus)s, %(JobResult)s, %(JobCreateDate)s, %(JobStartDate)s, %(JobEndDate)s)")

    def __init_(self):
        super().__init_()
        
    
    def insertJob(self,dataJob):
        now = datetime.now()
        dataJob['JobCreateDate'] = now
        dataJob['JobStartDate'] = None
        dataJob['JobEndDate'] = None
        dataJob['JobResult'] = None

        return super().insert(self.SQL_INSERT, dataJob)

  
    def updateJobById(self,dataJob,Id):
        updateSQLStart = "UPDATE DGJob SET "
        updateSQLEnd = " WHERE Id = %(Id)s"

        SQLMiddle = ''
        if ("JobStartDate" in  dataJob):
            SQLMiddle += ' JobStartDate =  %(JobStartDate)s,'
        if ("JobEndDate" in  dataJob):
            SQLMiddle += ' JobEndDate =  %(JobEndDate)s,'
        if ("JobStatus" in  dataJob):
            SQLMiddle += ' JobStatus =  %(JobStatus)s,'
        if ("JobResult" in  dataJob):
            SQLMiddle += ' JobResult =  %(JobResult)s,'

        if SQLMiddle != '':
            SQLMiddle = SQLMiddle[:-1]
            finalSql = updateSQLStart + SQLMiddle + updateSQLEnd
            dataJob['Id'] = Id
            return super().update(finalSql, dataJob, Id)
        else:
            return 0

    def deleteJobById(self,Id):
        updateSQL = "DELETE FROM DGJob WHERE Id = %(Id)s"
        data= {'Id' : Id}
        return super().update(updateSQL, data, Id)

    def createData(self, row):
        data = {'Id' : row[0],
                'JobType' : row[1],
                'JobOwner' : row[2],
                'JobData' : row[3],
                'JobStatus' : row[4],
                'JobResult' : row[5],
                'JobCreateDate' : row[6],
                'JobStartDate' : row[7],
                'JobEndDate' : row[8]}
        return data
    
    def getMostRecentPendingJob(self):
        sql = "SELECT * FROM DGJob WHERE JobStatus = 'PENDING' AND Id = (SELECT max(Id) FROM DGJob WHERE JobStatus = 'PENDING'  )"
        rows = super().query(sql, None)        
        if len(rows) > 0:
            return self.createData(rows[0])
        else:
            return None
    
    def getMostRecentJobForUser(self, username, status):
        in_params = ','.join("'" + id + "'" for id in status)
        sql = ("SELECT * FROM DGJob WHERE JobOwner = %(JobOwner)s AND JobStatus IN (" + in_params + ")"
                "AND Id = (SELECT max(Id) FROM DGJob WHERE JobOwner = %(JobOwner)s AND JobStatus IN (" + in_params + ") ) ")
        
        data= { 'JobOwner' : username}

        rows = super().query(sql, data)        
        if len(rows) > 0:
            return self.createData(rows[0])
        else:
            return None
        
    def getJobsForUser(self, username):
        sql = ("SELECT * FROM DGJob WHERE JobOwner = %(JobOwner)s ORDER BY JobCreateDate Desc")
        
        data= {'JobOwner' : username}
        rows = super().query(sql, data)
        ret = []        
        for row in rows:
            ret.append(self.createData(row))
        return ret
            
