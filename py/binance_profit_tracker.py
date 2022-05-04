import json
import ccxt
from ws4py.client.threadedclient import WebSocketClient
import os
import sys
import time
import datetime
from fonksiyonlar import *
basligi_degistir()

#------ config
config = ayarlari_config_json_dosyasindan_oku()
#okunan dosyadan configi serpistir
k_sifreli = config['binance_pumps']['api_key']
s_sifreli = config['binance_pumps']['api_secret']
target_coin = config['binance_pumps']['target_coin']
trade_with_real_account = str_to_bool(config['binance_pumps']['trade_with_real_account'])

pair=""

alinan_miktar = 0

k = sifre_coz(k_sifreli)
s = sifre_coz(s_sifreli)

exchange = ccxt.binance({
	'apiKey': k,
	'secret': s,
	'enableRateLimit': True,
	'options': { 'adjustForTimeDifference': True }	
})

target_altcoin=sys.argv[1] #1. parametre orn: LTC
ilk_price = float(sys.argv[2]) #2. parametre orn: 0.00210000

try: take_profit = float(sys.argv[3])
except: take_profit = 9999

try: stop_loss = float(sys.argv[4])
except: stop_loss = -9999
	
alinan_miktar = 0 #islem bilgileri sorgulanirken guncellenecek
satin_alinan_price = 0.0

def basla():
	oncelikle_islemi_dogrula()
	
def oncelikle_islemi_dogrula():
	global satin_alinan_price, alinan_miktar

	if trade_with_real_account:
		kac_saniyeye_kadar_iste_islem_bu_diyorum = 20
	else:
		kac_saniyeye_kadar_iste_islem_bu_diyorum = 60*60*24*7
		
	kontrol_sayisi = 0
	
	alim_tamamlandi_mi = False
	
	while (alim_tamamlandi_mi == False):
		try:
			global ilk_price
			kontrol_sayisi += 1
			
			#son islemi dogrulamaya calisiyorum
			suanki_timestamp = int(time.time())
			kac_dk_onceki_islemler_alinsin = 2
			
			symbol = (target_altcoin + "/" + target_coin).upper()
			since = suanki_timestamp - kac_dk_onceki_islemler_alinsin * 60
			limit = 1
			
			islem = exchange.fetch_my_trades(symbol,since,limit)
			son_islem = islem[0]
			
			ekrani_temizle()
			
			print("")
			print("last trade: " + son_islem['id'])
			print("===================================")
			print("symbol: " + son_islem['symbol'])
			print("side: " + son_islem['side'])
			alinan_miktar = float(son_islem['info']['qty'])
			print("qty: " + str(alinan_miktar))
			satin_alinan_price = float(son_islem['info']['price'])
			print("Price: " + str(ilk_price))

			islem_timestamp = int(son_islem['timestamp'] / 1000)
			saniye_farki = suanki_timestamp - islem_timestamp
			
			gecen_sure = str(datetime.timedelta(seconds=saniye_farki))
			
			print("passed time: " + gecen_sure)
			print("controlled: " + str(kontrol_sayisi))

			print("")
			print("Real account?")
			print("===================================")
			print(str(trade_with_real_account))
			
			alim_tamamlandi_mi = saniye_farki < kac_saniyeye_kadar_iste_islem_bu_diyorum
			print("")
			print("Order placed?")
			print("===================================")
			print(str(alim_tamamlandi_mi))
			
			if alim_tamamlandi_mi == False: time.sleep(1)
		except Exception as e:
			hata = str(e)
			if hata=="list index out of range":
				print("there is no info about this altcoin")
			else:
				print("error 4567: " + hata)
				
			time.sleep(1)
		
	#while dongusu gecildiyse alim tamamlandi demektir
	fiyatlari_canli_tutmak_icin_sockete_baglan()
	
	
def fiyatlari_canli_tutmak_icin_sockete_baglan():
	try:
		pair = (target_altcoin + target_coin).lower()
		ws = socket_baglantisi('wss://stream.binance.com:9443/ws/' + pair + '@ticker')
		ws.connect()
		ws.run_forever()
	except KeyboardInterrupt:
		ws.close()
		
canli_fiyatlar = {}
guncelleme_sayisi = 0
def fiyatlari_canli_tut(m):
	global canli_fiyatlar, satin_alinan_price, alinan_miktar
	
	veriler = m.data.decode("utf-8")
	json_tickerlar = json.loads(veriler)
	
	#satin alanlar (bid) (yesil) fiyatlari baz aliyorum
	son_price = float(json_tickerlar["b"])
	
	degisim24h = float(json_tickerlar["P"])
	kazanc_yuzdesi = format(degisim24h, '.2f')
	
	ekrani_temizle()
	
	print("")
	ask_fiyati = float(json_tickerlar["a"]) #satan
	bid_fiyati = float(json_tickerlar["b"]) #alan
	makas_araligi = (ask_fiyati - bid_fiyati) / ask_fiyati * 100
	
	print("")
	print(target_altcoin)
	print("===================================")
	print("Total trades: " + str(json_tickerlar["n"]))
	#print(kirmizi("ask: " + format(ask_fiyati, '.8f')))
	#print(yesil("bid: " + format(bid_fiyati, '.8f')))
	print("Spread: % " + format(makas_araligi, '.2f'))
	
	print("")
	print("Trying to get with this price")
	print("==================================")
	print(format(ilk_price, '.8f'))
	
	print("")
	print("Got it")
	print("==================================")
	print("Price : " + format(satin_alinan_price, '.8f'))
	print("Live price : " + format(son_price, '.8f'))
	
	print("")
	print("Profit")
	print("==================================")
	
	kazanc_yuzdesi = (son_price - satin_alinan_price) * 100 / satin_alinan_price
	if (kazanc_yuzdesi == 0):
		kazanc_yuzdesi = format(kazanc_yuzdesi, '.2f')
		kazanc_yuzdesi_yazisi = str("% " + str(kazanc_yuzdesi))
	elif (kazanc_yuzdesi > 0):
		kazanc_yuzdesi = format(kazanc_yuzdesi, '.2f')
		kazanc_yuzdesi_yazisi = yesil("% " + str(kazanc_yuzdesi))
	else:
		kazanc_yuzdesi = format(kazanc_yuzdesi, '.2f')
		kazanc_yuzdesi_yazisi = kirmizi("% " + str(kazanc_yuzdesi))

	print(kazanc_yuzdesi_yazisi)
	print("")
	
	#================= satis yap
	def satis_yap():
		#satis emri	
		pair = (target_altcoin + "/" + target_coin).upper()
	
		timestamp_islem_baslangici = time.time()

		if (trade_with_real_account):
			#satis emri giriyorum
			print("placing sell order..")
			satis_emri = exchange.create_market_sell_order(pair, alinan_miktar)
		else:
			#placing test order
			print("placing test order...")
			params = {'test': True,}
			print("pair: " + pair)
			satis_emri = exchange.create_order(pair, "market" , "sell", alinan_miktar, satin_alinan_price, params)

		#bilgileri ekrana yaz
		timestamp_islem_bitisi = time.time()
		satis_emri_kac_saniyede_girildi = float(format(timestamp_islem_bitisi - timestamp_islem_baslangici, '.2f'))
		print("")
		print ("================== Order Info ==================")
		print (satis_emri)
		print ("timestamp: " + str(timestamp_islem_bitisi))
		print ("time: " + str(full_tarih(timestamp_islem_bitisi)))
		print ("sold in: " + str(satis_emri_kac_saniyede_girildi) + " sn")
		print ("================== Order Info ==================")
		
		
		input("\ndone.")

	#================= satis yap
	
	kazanc_yuzdesi = float(kazanc_yuzdesi)
	#satis stratejisi
	
	if (kazanc_yuzdesi <= stop_loss):
		print("stop loss order activated..")
		satis_yap()
	elif (kazanc_yuzdesi >= take_profit):
		print("taking profit order activated..")
		satis_yap()
	else:
		take_profit_belirtildi_mi = take_profit != 9999
		stop_loss_belirtildi_mi = stop_loss != -9999
		if take_profit_belirtildi_mi or stop_loss_belirtildi_mi:
			print("Strategy")
			print("====================")
			if take_profit_belirtildi_mi:
				print("take profit: %" + str(take_profit))
			if stop_loss_belirtildi_mi:
				print("stop loss: %" + str(stop_loss))

	
class socket_baglantisi(WebSocketClient):
	def closed(self, code, reason=None):
		print ("socket conenction is closed", code, reason)
	def received_message(self, m):
		fiyatlari_canli_tut(m)
		
def full_tarih(timestamp=0):
	if (timestamp == 0): timestamp = time.time()
	return(datetime.datetime.fromtimestamp(int(timestamp)).strftime('%d.%m.%y-%H.%M.%S'))
	
if __name__ == '__main__':	
	basla()
	