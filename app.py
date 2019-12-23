from flask import Flask, request, redirect

app = Flask(__name__)


@app.route('/get_data', methods=['POST', 'GET'])
def get_data():
    import json

    path = '/Users/mindyp/Downloads/PIPtagCode/ReceiverCode/testRun.txt'
    #six_list = []
    #one_list = []
    # json file save humidity and temp
    two_feature = []
    # json file save light
    one_feature = []

    with open(path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            data_tmp = {}
            light_tmp = {}
            a = line.split('\t')
            if len(a)<7:
                continue

            tx = a[3]  # a[3:4] TX:03406 or 03401
            #ts = a[0]  # TS
            # print(ts)
            # print(a)
            if not a[5].find('BAD'):
                continue
            
            print(a)
            try:
                # process the txt data
                b = a[6].split('  | ')[1].split(' ')
                # save two features humidity and temp
                data_tmp['TS'] = int(a[0].strip('TS:'))
                data_tmp['temp'] = float(b[3])
                #print(b[3])
                data_tmp['humidity'] = float(b[5].strip('\n'))
                # save feature light
                light_tmp['TS'] = int(a[0].strip('TS:'))
                light_tmp['light'] = float(b[1])
                # print(data_tmp)
                #print(data_tmp['humidity'])

            except IndexError:
                pass
            if tx == 'TX:03406':
                #  print(tx)
                if len(light_tmp) == 2:
                    one_feature.append(light_tmp)  # 将其添加在列表之中
                continue
            #         line = f.readline()
            else:
                #if not data_tmp:
                if len(data_tmp)<3:
                    continue
                #print(len(data_tmp))
                two_feature.append(data_tmp)
                #continue

    # unnify length
    #two_feature.pop(-1)
    len_one = len(one_feature)
    len_two = len(two_feature)
    if len_one > len_two:
        one_feature = one_feature[:len_two]
    else:
        two_feature = two_feature[:len_one]

    '''
    insert a full three feature list
    Here we assume the feature between two TS obey a linear function
    And what we do is to predict the light feature value at TS of two feature
    We want to use decisiontree regresion to predict the value at a certain TS
    '''

    from sklearn import tree

   # import pandas as pd
    import numpy as np

    train_X = []
    train_Y = []
    for light in one_feature:
        train_Y.append(light['light'])
        train_X.append(light['TS'])

    pred_X = []
    for pTS in two_feature:
        # print(pTS)
        pred_X.append(pTS['TS'])

    X = np.array(train_X).reshape(-1, 1)
    Y = np.array(train_Y)
    pX = np.array(pred_X).reshape(-1, 1)

    #print(X.shape,Y.shape)
    model = tree.DecisionTreeRegressor()
    model.fit(X, Y)

    pre_light = model.predict(pX)

    # now we create the final list

    whole_list = []
    for i in range(0, len(two_feature)):
        tmp_3 = two_feature[i]
        tmp_3['light'] = round(pre_light[i],1)
        #print(tmp_3['light'])
        whole_list.append(tmp_3)

    whole_list_json = json.dumps(whole_list)
    print(len(whole_list))
    filename = open('/Users/mindyp/Downloads/jsonFile/alldatawith3feature.json', 'w')  # dict转josn
    filename.write(whole_list_json)
    filename.close()

    return 'Hello World'


#app.run(debug=True, port=8000)

get_data()
