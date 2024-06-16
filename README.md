# Github Anomaly Detection
This is Michael Millich's homework assignment for Legit security.

This project provides a command line application
that detects and notifies suspicious behavior in an integrated GitHub organization.

**what is suspicious behavior**
1. pushing code between 14:00-16:00
2. create a team with the prefix “hacker”
3. creating a repository and deleting it in less than 10 minutes

**note**

currently the system is developed on linux - ubuntu 22 and is tested on this environment.

### How to use:
1. clone the repository to your computer
   1. `mkdir millich_homework`
   2. `cd millich_homework`
   3. `git clone https://github.com/MichaelMilich/LegitExcersize.git`
2. To use the same webhooks for the organization created to develop this app, use my `private_config.json` file that is provided separately.
   1. otherwise create your own `private_config.json` with your own {  "GITHUB_SECRET": "your_secret"}.
   2. This is a must for the code to run.
3. run `ngrok http --domain=model-weasel-hopefully.ngrok-free.app 5000` to start connecting the server to your localhost.
   1. **note:** you can change the port number from `5000` to what you want, but then you must change it also in step 4.
4. run `python3 github_anomaly_detection.py 5000` to start the command line application.

