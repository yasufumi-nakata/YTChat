from Xyoutube import XYoutube
import json, requests, os,sys,time

#サンプルURL
url = 'https://www.youtube.com/watch?v=ZwUndsT-XvQ'

#チャットログ入手用URL
chatURL = 'https://www.youtube.com/live_chat_replay/get_live_chat_replay?'

#テンプレート
PR = {
    'continuation':'op2w0wQ9GiBDZzhhRFFvTGQyWTBPRkUzY0RSa1ZFVWdBUSUzRCUzRCiR7eoPMAA4AEAASANSAGAEaAByBAgEEAB4AA%3D%3D',
    'playerOffsetMs':'0',
    'hidden':'False',
    'pbj':'1'}


def setparam(pr):
    #パラメータを繋げる
    p = ''
    for i in pr:
        p += i + '=' +pr[i]+ '&'
    return p[:-1]

def init(url):
    #初期化 
    r = XYoutube()
    r.pr = PR

    r.url = url
    r.get()
    v = r.getVideoInfo()
    #チャット取得用 continuationのパラメータを入手
    con = v\
        ['ytInitialData']\
            ['contents']\
            ['twoColumnWatchNextResults']\
                ['conversationBar']\
                    ['liveChatRenderer']\
                        ['header']\
                            ['liveChatHeaderRenderer']['viewSelector']['sortFilterSubMenuRenderer']['subMenuItems'][1]\
                                   ['continuation']['reloadContinuationData']['continuation']
    r.pr['continuation'] = con

    r.url = chatURL+setparam(r.pr)
    res = r.get()
    
    if res:
        vid = v['ytplayerconfig']['args']['video_id']
        try:
            #LIVE ID名のディレクトリの作成
            os.mkdir(vid)
        except:
            pass
        with open(os.path.join(vid,'yt__init__'), 'w',encoding='utf-8') as f:
            json.dump(json.loads(v),f, indent=4, ensure_ascii=False)
        with open(os.path.join(vid,'0.json'), 'w',encoding='utf-8') as f:
            json.dump(json.loads(res),f, indent=4, ensure_ascii=False)
        return r, vid
    else:
        #リクエスト失敗で終了 (ここ怪しい)
        print('cannot get first chats')
        print('end')

        exit()

def Lcontinueparam(vid,i):
    #load continue param 次のパラメータの整理
    with open(os.path.join(vid,'{}.json'.format(i)), 'r', encoding='utf-8') as f:
        a = json.load(f)
    try:
        con = a['response']['continuationContents']['liveChatContinuation']['continuations'][0]['liveChatReplayContinuationData']['continuation']
        chat = a['response']['continuationContents']['liveChatContinuation']['actions']
        offsetTMS = chat[len(chat)-1]['replayChatItemAction']['videoOffsetTimeMsec']
    except KeyError:
        #パラメータの取得に失敗するまで続ける　終了
        print('get comment complete')
        print('end')
        exit()
    return con, offsetTMS


def main(url):
    #LIVE IDとリクエスト用オブジェクトを初期化
    r, vid = init(url)
    i = 0
    while True:
        #continuation, playerOffsetMs の更新
        r.pr['continuation'], r.pr['playerOffsetMs'] = Lcontinueparam(vid, i)
        r.url = chatURL+setparam(r.pr)
        print('{}:request: {}'.format(i,r.pr['playerOffsetMs']))
        i+=1
        res = r.get()
        time.sleep(5)
        if res:
            with open(os.path.join(vid,'{}.json'.format(i)), 'w', encoding='utf-8') as f:
               json.dump(json.loads(res),f, indent=4, ensure_ascii=False)
        else:
            print('{} request error'.format(i))
            exit()

if __name__ =='__main__':
    a = sys.argv
    a.pop(0)
    while len(a) > 0 :
        main(a[0])
        a.pop(0)
