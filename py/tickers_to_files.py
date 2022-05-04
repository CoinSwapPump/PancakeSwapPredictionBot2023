import json
import ccxt
from ws4py.client.threadedclient import WebSocketClient
import os
from fonksiyonlar import *
exchange = ccxt.binance()
tickerlar = exchange.fetch_tickers()
currencies = exchange.currencies

target_coin = "BTC"

from subprocess import check_output
tickerlar_klasoru = "py/tickerlar"
try:
	check_output('rmdir "' + tickerlar_klasoru + '" /s /q', shell=True)
	print("removed old prices")
except: ""
try:
	check_output('mkdir "' + tickerlar_klasoru + '"', shell=True)
	print("created new folder")
except: ""
		
def basla():
	print("caching the tickers..")
	fiyatlari_canli_tutmak_icin_sockete_baglan()
		
def tickeri_dosyaya_yaz(ticker,ne):
	dosya_full_adres = tickerlar_klasoru + "\\" + ticker + ".txt"
	file = open(dosya_full_adres,"w")
	file.write(ne)
	file.close()
	
def fiyatlari_canli_tutmak_icin_sockete_baglan():
	try:
		ws = socket_baglantisi('wss://stream.binance.com:9443/ws/!ticker@arr')
		ws.connect()
		ws.run_forever()
	except KeyboardInterrupt:
		ws.close()
		
canli_fiyatlar = {}
guncelleme_sayisi = 0
def fiyatlari_canli_tut(m):
	global canli_fiyatlar
	veriler = m.data.decode("utf-8")
	json_tickerlar = json.loads(veriler)
	for satir in json_tickerlar:
		pair = satir["s"]
		if (pair.endswith(target_coin)):
			#bazi altcoinlerin id ve code adlari degisIk oluyor
			#ornegin nano yerine xrb yazilmali burda id'den code'a ceviriyorum
			coin = pair.replace(target_coin,"").upper()
			coin = coin_id_yi_code_a_cevir(coin)
			pair = coin + target_coin
			fiyat = satir["b"]
			if (not pair in canli_fiyatlar) or (canli_fiyatlar[pair] != fiyat):
				canli_fiyatlar[pair] = fiyat
				tickeri_dosyaya_yaz(pair,fiyat)
				
	global guncelleme_sayisi
	guncelleme_sayisi += 1
	
	restart_zamanlarindaysam_programi_yeniden_ac()
	
	print("updated " + str(guncelleme_sayisi))
	
	#print(canli_fiyatlar["ETH/BTC"])
	
class socket_baglantisi(WebSocketClient):
	def closed(self, code, reason=None):
		print ("socket connection is closed", code, reason)
	def received_message(self, m):
		fiyatlari_canli_tut(m)
		
		
def coin_id_yi_code_a_cevir(coin):
	#Bazi altcoinler isim degisIkligi yapiyor
	#ornegin Nano 'yu satin alma emri verirken Xrb code adiyla girmek lazim
	#currencies["XRB"]["id"]
	for currency in currencies:
		id = currencies[currency]["id"]
		code = currencies[currency]["code"]
		if (id == coin):
			return (code)
			break
			
if __name__ == '__main__':	
	basla()
	