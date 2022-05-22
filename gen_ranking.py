import os
import json
import collections
import bisect
import csv
import get_submissions

def _set_rank (scoreboard):
    all_score = [v['total'] for k,v in scoreboard.items()]
    contestantNum = len(scoreboard)
    all_score.sort()
    for info in scoreboard.values():
        info['rank'] = contestantNum-bisect.bisect_right(all_score,info['total'])+1

def _gen_scoreboard (data):
    scoreboard = collections.defaultdict((lambda:{
        "rank":0,
        "total":0,
        "score_details":dict([(l,{"problem_score": 0,"subtask_details": []}) for l in sorted(all_lable)])
    }))
    all_lable = set([x[2] for x in data])

    for sub in data:
        handle = sub[0]
        lable = sub[2]
        score_list = sub[4]

        if (len(scoreboard[handle]['score_details'][lable]['subtask_details']) == 0):
            scoreboard[handle]['score_details'][lable]['subtask_details'] = score_list
        else:
            for i in range(len(score_list)):
                scoreboard[handle]["score_details"][lable]["subtask_details"][i] = max(
                    scoreboard[handle]["score_details"][lable]["subtask_details"][i],
                    score_list[i]
                )
        
        scoreboard[handle]["total"] -= scoreboard[handle]["score_details"][lable]["problem_score"]
        scoreboard[handle]["score_details"][lable]["problem_score"] = sum(scoreboard[handle]["score_details"][lable]["subtask_details"])
        scoreboard[handle]["total"] += scoreboard[handle]["score_details"][lable]["problem_score"]

    _set_rank(scoreboard)

    return scoreboard,all_lable

def _gen_table (scoreboard,all_lable):
    table = []
    for handle,info in scoreboard.items():
        table.append(
            [info['rank'], handle] +
            [info['score_details'][l]['problem_score'] for l in sorted(all_lable)] +
            [info['total']]
        )
    table.sort()
    return table

if __name__ == '__main__':
    if os.path.isfile('submissions.json'):
        with open('submissions.json','r') as submissions_txt:
            data = json.loads(submissions_txt.read())
    else:
        data = get_submissions.get_submissions()

    scoreboard,all_lable = _gen_scoreboard(data)
    with open('score_status.json','w') as jsonfile:
        jsonfile.write(json.dumps(scoreboard, indent=4, sort_keys=True));
        
    table = _gen_table(scoreboard,all_lable)
    with open('ranking.csv','w',newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['rank', 'handle']+list(sorted(all_lable))+['total'])
        for row in table:
            writer.writerow(row)