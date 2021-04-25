# Multifunctional skill for Yandex-Alice

# installation
```
git clone https://github.com/kldd0/Alice-multiskill.git
```
# Start
#### to run it locally, you need to create a file ```.env``` and put it in it api-keys
#### of the following services: Yandex-geocoder, Yandex-maps, VirusTotal, Yandex-weather
```
API_KEY={API-KEY}
WEATHER_API_KEY={API-KEY}
GEOCODER_API_KEY={API-KEY}
SKILL_ID={API-KEY}
ACCESS_TOKEN={API-KEY}
TRANSLATOR_TOKEN={API-KEY}
```
#### then you can use ngrok to run
#### default port for work is ```8989```
#### you can change it in ```main.py```
```python
if __name__ == "__main__":
    app.run(port=8989)
```



<h5>--Project for Yandex Lyceum--</h5>
