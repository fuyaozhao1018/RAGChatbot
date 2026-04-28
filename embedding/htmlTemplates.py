css = '''
<style>
.stApp {
    background: #f7f7f4;
}

.block-container {
    max-width: 980px;
    padding-top: 2rem;
}

.chat-message {
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    display: flex;
    border: 1px solid #d9d9d4;
}

.chat-message.user {
    background-color: #222831;
}

.chat-message.bot {
    background-color: #ffffff;
}

.chat-message .avatar {
    width: 64px;
    flex: 0 0 64px;
}

.chat-message .avatar img {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    object-fit: cover;
}

.chat-message .message {
    width: calc(100% - 64px);
    padding: 0 1rem;
    color: #1f2328;
    line-height: 1.55;
    overflow-wrap: anywhere;
}

.chat-message.user .message {
    color: #ffffff;
}
</style>
'''

bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="https://upload.wikimedia.org/wikipedia/commons/0/0c/Chatbot_img.png">
    </div>
    <div class="message">{{MSG}}</div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="avatar">
        <img src="https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png">
    </div>
    <div class="message">{{MSG}}</div>
</div>
'''
