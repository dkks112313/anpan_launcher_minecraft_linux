import uuid

options = {
    'username': '',
    'uuid': str(uuid.uuid4()),
    'token': '',
    'jvmArguments': []
}
settings = {
    'snapshot': bool(),
    'alpha': bool(),
    'console': bool(),
    'data': bool(),
    'git': bool(),
    'minecraft_directory': '',
    'version': '',
    'status': bool(),
    'mods': ''
}
forge = ['1.1', '1.2.3', '1.2.4', '1.2.5', '1.3.2', '1.4.0', '1.4.1',
         '1.4.2', '1.4.3', '1.4.4', '1.4.5', '1.4.6', '1.4.7', '1.5.1', '1.5.2',
         '1.5', '1.6.1', '1.6.2', '1.6.3', '1.6.4', '1.7.10_pre4', '1.7.2',
         '1.7.10', '1.8.8', '1.8.9', '1.8', '1.9.4', '1.9', '1.10.2', '1.10',
         '1.11.2', '1.11', '1.12.1', '1.12.2', '1.12']
