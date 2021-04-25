# Multifunctional skill for Yandex-Alice
![https://img.shields.io/github/stars/kldd0/Alice-multiskill?style=social](https://img.shields.io/github/stars/kldd0/Alice-multiskill?style=social)
`Language:` ![https://img.shields.io/badge/Python-3.8-blue](https://img.shields.io/badge/Python-3.8-blue)
`Status:` ![https://img.shields.io/badge/Realese-Yes-green](https://img.shields.io/badge/Realese-Yes-green)

# Installation
```
git clone https://github.com/kldd0/Alice-multiskill.git
```
# Start
#### to run it locally, you need to create a file ```.env``` and put it in it api-keys of the following services:
#### Yandex-geocoder, Yandex-maps, VirusTotal, Yandex-weather
> the file should look like in the exhibition
```
API_KEY={API-KEY}
WEATHER_API_KEY={API-KEY}
GEOCODER_API_KEY={API-KEY}
SKILL_ID={API-KEY}
ACCESS_TOKEN={API-KEY}
TRANSLATOR_TOKEN={API-KEY}
```
#### then you can use ```ngrok``` to run
#### default port for work is ```8989```
#### you can change it in ```main.py```
```python
if __name__ == "__main__":
    app.run(port=8989)
```
#### then you need to run `main.py` and put the url of ngrok in form `Backend` as `Webhook URL` in Yandex-dialogs
#### example of ngrok address
```
https://e0aab85a27ef.ngrok.io
```




> Project for Yandex Lyceum
