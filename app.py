from flask import Flask, request, redirect, url_for, render_template_string, jsonify
import requests
import time
from collections import defaultdict
import pandas as pd
from io import StringIO

app = Flask(__name__)

# Common Headers
headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'referer': 'www.google.com'
}

# डेटा स्टोरेज (In-memory)
group_data = {
    'members': defaultdict(int),
    'messages': [],
    'analytics': {'total_comments': 0, 'active_users': set()}
}

@app.route('/')
def index():
    # टॉप मेंबर्स की लिस्ट तैयार करना
    top_members = sorted(group_data['members'].items(), key=lambda x: x[1], reverse=True)[:10]
    # स्पैम मैसेजेस फिल्टर करना
    spam_messages = [msg for msg in group_data['messages'] if "http://" in msg['text']][:20]
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DEVIL POST + ANALYTICS</title>
    <style>
        body {
            background-image: url('https://i.ibb.co/qMNy8Lh/received-437195329281136.jpg');
            background-size: cover;
            background-repeat: no-repeat;
            color: white;
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
            background: rgba(0, 0, 0, 0.7);
        }
        .header h1 {
            margin: 0;
            font-size: 24px;
        }
        .container {
            background-color: rgba(0, 0, 0, 0.7);
            padding: 20px;
            border-radius: 10px;
            max-width: 1200px;
            margin: 40px auto;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        .tab {
            overflow: hidden;
            border: 1px solid #444;
            background-color: #333;
        }
        .tab button {
            background-color: inherit;
            float: left;
            border: none;
            outline: none;
            cursor: pointer;
            padding: 14px 16px;
            transition: 0.3s;
            color: white;
        }
        .tab button:hover {
            background-color: #555;
        }
        .tab button.active {
            background-color: #4CAF50;
        }
        .tabcontent {
            display: none;
            padding: 20px;
            border: 1px solid #444;
            border-top: none;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background-color: rgba(0, 0, 0, 0.5);
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #444;
        }
        th {
            background-color: #4CAF50;
            color: white;
        }
        tr:hover {
            background-color: #555;
        }
        .form-group {
            margin-bottom: 15px;
        }
        input, select, textarea {
            width: 100%;
            padding: 10px;
            background: #333;
            color: white;
            border: 1px solid #444;
        }
        button {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            margin-top: 10px;
        }
        .btn-submit {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            cursor: pointer;
            border-radius: 5px;
            width: 100%;
        }
        footer {
            text-align: center;
            padding: 20px;
            background-color: rgba(0, 0, 0, 0.7);
            margin-top: auto;
        }
    </style>
</head>
<body>
    <header class="header">
        <h1 style="color: red;">WARRIOR RULEX DEVIL INSIDE</h1>
        <h1 style="color: blue;">DEVIL POST SERVER (ADVANCED)</h1>
    </header>

    <div class="container">
        <div class="tab">
            <button class="tablinks active" onclick="openTab(event, 'PostTool')">पोस्ट टूल</button>
            <button class="tablinks" onclick="openTab(event, 'Analytics')">एनालिटिक्स</button>
            <button class="tablinks" onclick="openTab(event, 'GroupMgmt')">ग्रुप मैनेजमेंट</button>
        </div>

        <!-- पोस्टिंग टूल -->
        <div id="PostTool" class="tabcontent" style="display:block;">
            <h2>डेविल पोस्ट टूल</h2>
            <form action="/post" method="post" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="threadId">POST ID:</label>
                    <input type="text" class="form-control" id="threadId" name="threadId" required>
                </div>
                <div class="form-group">
                    <label for="kidx">Enter Hater Name:</label>
                    <input type="text" class="form-control" id="kidx" name="kidx" required>
                </div>
                <div class="form-group">
                    <label for="method">Choose Method:</label>
                    <select class="form-control" id="method" name="method" required onchange="toggleFileInputs()">
                        <option value="token">Token</option>
                        <option value="cookies">Cookies</option>
                    </select>
                </div>
                <div class="form-group" id="tokenFileDiv">
                    <label for="tokenFile">Select Your Tokens File:</label>
                    <input type="file" class="form-control" id="tokenFile" name="tokenFile" accept=".txt">
                </div>
                <div class="form-group" id="cookiesFileDiv" style="display: none;">
                    <label for="cookiesFile">Select Your Cookies File:</label>
                    <input type="file" class="form-control" id="cookiesFile" name="cookiesFile" accept=".txt">
                </div>
                <div class="form-group">
                    <label for="commentsFile">Select Your Comments File:</label>
                    <input type="file" class="form-control" id="commentsFile" name="commentsFile" accept=".txt" required>
                </div>
                <div class="form-group">
                    <label for="time">Speed in Seconds (minimum 20 second):</label>
                    <input type="number" class="form-control" id="time" name="time" required>
                </div>
                <button type="submit" class="btn-submit">Submit Your Details</button>
            </form>
        </div>

        <!-- एनालिटिक्स डैशबोर्ड -->
        <div id="Analytics" class="tabcontent">
            <h2>ग्रुप एनालिटिक्स</h2>
            <div>
                <h3>टॉप मेंबर्स (कमेंट काउंट)</h3>
                <table id="memberTable">
                    <tr><th>नाम</th><th>कमेंट्स</th></tr>
                    {% for member, count in top_members %}
                    <tr><td>{{ member }}</td><td>{{ count }}</td></tr>
                    {% endfor %}
                </table>
            </div>
            <button onclick="exportData('members')">एक्सपोर्ट टू एक्सेल</button>
            
            <h3 style="margin-top: 30px;">स्टैटिस्टिक्स</h3>
            <table>
                <tr><th>टोटल कमेंट्स</th><td>{{ analytics.total_comments }}</td></tr>
                <tr><th>एक्टिव यूजर्स</th><td>{{ analytics.active_users|length }}</td></tr>
            </table>
        </div>

        <!-- ग्रुप मैनेजमेंट -->
        <div id="GroupMgmt" class="tabcontent">
            <h2>ग्रुप मॉडरेशन</h2>
            <form action="/ban_user" method="post">
                <div class="form-group">
                    <label for="userId">यूजर आईडी:</label>
                    <input type="text" id="userId" name="userId" required>
                </div>
                <button type="submit">बैन यूजर</button>
            </form>
            <h3>स्पैम डिटेक्शन (आखिरी 20 मैसेज)</h3>
            <table id="spamTable">
                <tr><th>मैसेज</th><th>एक्शन</th></tr>
                {% for msg in spam_messages %}
                <tr>
                    <td>{{ msg.text }}</td>
                    <td><button onclick="deleteMsg('{{ msg.id }}')">डिलीट</button></td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </div>

    <footer>
        <p style="color: #FF5733;">Advanced Post Loader & Analytics Tool</p>
        <p>Made with ❤️ by devil</p>
    </footer>

    <script>
        function openTab(evt, tabName) {
            var tabcontent = document.getElementsByClassName("tabcontent");
            for (var i = 0; i < tabcontent.length; i++) {
                tabcontent[i].style.display = "none";
            }
            document.getElementById(tabName).style.display = "block";
        }
        
        function toggleFileInputs() {
            var method = document.getElementById('method').value;
            if (method === 'token') {
                document.getElementById('tokenFileDiv').style.display = 'block';
                document.getElementById('cookiesFileDiv').style.display = 'none';
            } else {
                document.getElementById('tokenFileDiv').style.display = 'none';
                document.getElementById('cookiesFileDiv').style.display = 'block';
            }
        }
        
        function exportData(type) {
            fetch(`/export/${type}`).then(res => res.blob()).then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${type}_report.xlsx`;
                a.click();
            });
        }
        
        function deleteMsg(msgId) {
            fetch(`/delete_msg/${msgId}`, {method: 'POST'})
                .then(response => alert('Message deleted!'))
                .then(() => location.reload());
        }
    </script>
</body>
</html>
''', top_members=top_members, spam_messages=spam_messages, analytics=group_data['analytics'])

@app.route('/post', methods=['POST'])
def post_comments():
    method = request.form.get('method')
    thread_id = request.form.get('threadId')
    mn = request.form.get('kidx')
    time_interval = int(request.form.get('time'))

    comments_file = request.files['commentsFile']
    comments = comments_file.read().decode().splitlines()

    if method == 'token':
        token_file = request.files['tokenFile']
        credentials = token_file.read().decode().splitlines()
        credentials_type = 'access_token'
    else:
        cookies_file = request.files['cookiesFile']
        credentials = cookies_file.read().decode().splitlines()
        credentials_type = 'Cookie'

    num_comments = len(comments)
    num_credentials = len(credentials)

    post_url = f'https://graph.facebook.com/v23.0/{thread_id}/comments'
    haters_name = mn
    speed = time_interval

    # डेटा कलेक्शन
    group_data['members'][haters_name] += num_comments
    group_data['analytics']['total_comments'] += num_comments
    group_data['analytics']['active_users'].add(haters_name)
    
    for comment_index in range(num_comments):
        credential_index = comment_index % num_credentials
        credential = credentials[credential_index]
        
        parameters = {'message': haters_name + ' ' + comments[comment_index].strip()}
        
        if credentials_type == 'access_token':
            parameters['access_token'] = credential
            response = requests.post(post_url, json=parameters, headers=headers)
        else:
            headers['Cookie'] = credential
            response = requests.post(post_url, data=parameters, headers=headers)

        # मैसेज डेटा स्टोर करें
        group_data['messages'].append({
            'id': f"msg_{time.time()}",
            'text': parameters['message'],
            'user': haters_name,
            'time': time.strftime("%Y-%m-%d %H:%M:%S")
        })
        
        time.sleep(speed)
    
    return redirect('/')

@app.route('/export/<data_type>')
def export_data(data_type):
    if data_type == 'members':
        df = pd.DataFrame(list(group_data['members'].items()), columns=['Member', 'Comments'])
    else:
        df = pd.DataFrame(group_data['messages'])
    
    output = StringIO()
    df.to_excel(output, index=False)
    return app.response_class(
        output.getvalue(),
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': f'attachment;filename={data_type}_report.xlsx'}
    )

@app.route('/ban_user', methods=['POST'])
def ban_user():
    user_id = request.form.get('userId')
    # यहां आप Facebook API का उपयोग करके यूजर को बैन कर सकते हैं
    return jsonify({'status': f'User {user_id} banned successfully'})

@app.route('/delete_msg/<msg_id>', methods=['POST'])
def delete_msg(msg_id):
    # यहां आप Facebook API का उपयोग करके मैसेज डिलीट कर सकते हैं
    group_data['messages'] = [msg for msg in group_data['messages'] if msg['id'] != msg_id]
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
