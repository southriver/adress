from datetime import datetime
import os
from pathlib import Path
from model.PredictMMSE import PredictMMSEProcess
from model.db.DGJobAccess import DGJobAccess


def consumeQueue():
    access = DGJobAccess()
    row = access.getMostRecentPendingJob()
    if row == None:
        print ('No jobs to process, exiting')
        return
    
    try:
        id = row['Id']
        audioFileName = row['JobData']  #data
        print ('Processing job id: ', id, ' for filename: ', audioFileName)
        THIS_FOLDER = Path(__file__).parent.resolve()
        filename = THIS_FOLDER / 'MMSE' / audioFileName
        row['JobStartDate'] = datetime.now()
        row['JobStatus'] = 'IN PROGRESS'
        access.updateJobById(row, id)
        
        if not os.path.exists(filename):
            print ('File not found')
            row['JobStatus'] = 'ERROR'
            row['JobResult'] = 'File not found'
            row['JobEndDate'] = datetime.now()
            access.updateJobById(row, id)
            return
        
        process = PredictMMSEProcess()
        mmse = process.predict(audio_file=filename)
        print ('Calculated MMSE : ', str(mmse))
        row['JobStatus'] = 'APPLIED'
        row['JobResult'] = str(mmse)
        row['JobEndDate'] = datetime.now()
        access.updateJobById(row, id)
        # if os.path.exists(filename):
        #     os.remove(filename)
    except Exception as error:
        print ('Error ', str(error))
        row['JobStatus'] = 'ERROR'
        row['JobResult'] = str(error)
        row['JobEndDate'] = datetime.now()
        access.updateJobById(row, id)

# consumeQueue()