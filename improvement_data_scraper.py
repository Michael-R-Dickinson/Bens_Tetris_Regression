import os
import requests
import json
from datetime import datetime

running_dir = os.path.dirname(os.path.realpath(__file__))


def grab_player_stats(username):
    url = f'https://jstris.jezevec10.com/u/{username}/stats?mode=1&displayAll=true'
    page = requests.get(url).text
    data = json.loads(page.split('var data =')[1].split('</script>')[0][2:-7])

    if not os.path.exists(os.path.join(running_dir, 'improvement_data')):
        os.mkdir(os.path.join(running_dir, 'improvement_data'))

    with open(os.path.join(running_dir, 'improvement_data', f'jstris_data-{username}.tsv'), 'w') as f:
        f.write('Time\tReplay\tPlayed\n')
        for i in data['skyline'] + data['unused']:
            f.write(str(i['y'])+'\t'+str(i['id'])+'\t' +
                    datetime.utcfromtimestamp(i['x']).strftime('%Y-%m-%d %H:%M:%S')+'\n')


# if __name__ == '__main__':
#     running_dir = os.path.dirname(os.path.realpath(__file__))
