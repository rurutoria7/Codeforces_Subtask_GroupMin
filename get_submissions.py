# by SorahISA
import getpass, re, json
from requests import Session
from hashlib import sha512
from urllib.parse import urlencode
from time import time

def _login(s, handle, password):
    res = s.get('https://codeforces.com/enter')
    csrf_token = re.findall('<meta name="X-Csrf-Token" content="(.{32})"/>', res.text)[0]
    data = {
        'csrf_token': csrf_token,
        'action': 'enter',
        'ftaa': '',
        'bfaa': '',
        'handleOrEmail': handle,
        'password': password
    }
    res = s.post('https://codeforces.com/enter', data = data)
    assert 'Logout' in res.text
 
def _get_submission_detail(s, ID):
    res = s.get('https://codeforces.com')
    csrf_token = re.findall('<meta name="X-Csrf-Token" content="(.{32})"/>', res.text)[0]
    data = {
        'csrf_token': csrf_token,
        'submissionId': ID,
    }
    res = s.post('https://codeforces.com/group/2J8fZE6dA0/data/judgeProtocol', data = data) # CHANGE IT
    return res.text
 
def _logout(s):
    res = s.get('https://codeforces.com')
    link = re.findall('<a href="(/.{32}/logout)">Logout</a>', res.text)[0]
    res = s.get('https://codeforces.com' + link)
    assert 'Logout' not in res.text
 
def _get_submission_ids(s, contestId):
    key = '62abf96f60daba163e09c91cc9639cc41162a209' # CHANGE IT
    secret = 'd5f8bc4058c413c410cbeb01d2e5e2f212c3b192' # CHANGE IT
    # contestId = 316970
    data = urlencode({
        'apiKey': key,
        'contestId': contestId,
        # 'count': 100,
        # 'from': 1,
        'time': int(time())
    })
    methods = 'contest.status'
    apiSig = sha512(f'123456/{methods}?{data}#{secret}'.encode()).hexdigest()
    res = s.get(f'https://codeforces.com/api/{methods}?{data}', params = {'apiSig': '123456' + apiSig})
    api_json = json.loads(res.text)
    submission_ids = []
    for submission_info in api_json['result']:
        if (submission_info['author']['participantType'] == 'MANAGER'):
            continue
        if (submission_info['relativeTimeSeconds'] == 2147483647):
            continue
        # if (submission_info['points'] == 0.0):
            # continue
        handle = submission_info['author']['members'][0]['handle']
        participant_type = submission_info['author']['participantType']
        problem_index = submission_info['problem']['index']
        submission_time = submission_info['relativeTimeSeconds']
        submission_id = submission_info['id']
        submission_ids.append([handle, participant_type, problem_index, submission_time, submission_id])
    return submission_ids
 
def _process_submission(submission):
    start = 0
    place = submission.find('Group')
    subtasks = []
    while (place >= 0):
        start = place+1
        place = submission.find(':', start)
        for i in range(place+2, place+10):
            if (submission[i] == ' '):
                subtasks.append(float(submission[place+2 : i]))
                break
        place = submission.find('Group', start)
    return subtasks
 
#if __name__ == '__main__':
def get_submissions():
    # handle = input('enter handle: ')
    handle = 'aruphoria' # CHANGE IT
    password = getpass.getpass('enter password: ')
    contestId = 367020
    
    s = Session()
    _login(s, handle, password)
    submission_ids = _get_submission_ids(s, contestId);
    data = [[x[0], x[1], x[2], x[3], _process_submission(_get_submission_detail(s, x[4]))] for x in submission_ids]
    #file = open(str(contestId) + '.txt', 'w')
    #for submission in data:
        #file.write(str(submission) + '\n')
  
    with open('submissions.json','w') as fout:
        data_json = json.dumps(data)
        fout.write(data_json)
        
    _logout(s)
    return data
