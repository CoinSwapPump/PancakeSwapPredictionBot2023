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
k_sifreli = config['buy_with_okex']['api_key']
s_sifreli = config['buy_with_okex']['api_secret']
target_coin = config['buy_with_okex']['target_coin']
trade_with_real_account = str_to_bool(config['buy_with_okex']['trade_with_real_account'])
#------ config

k = sifre_coz(k_sifreli)
s = sifre_coz(s_sifreli)

exchange = ccxt.okex({
	'apiKey': k,
	'secret': s,
	'enableRateLimit': True,
	'options': { 'adjustForTimeDifference': True }	
})

target_coin = "BTC"
target_altcoin=sys.argv[1] #1. parametre orn: LTC
order_id = sys.argv[2] #2. parametre orn: 565374575365745435
pair = (target_altcoin + "/" + target_coin).upper()
try: take_profit = float(sys.argv[3])
except: take_profit = 9999

try: stop_loss = float(sys.argv[4])
except: stop_loss = -9999
	
alinan_miktar = 0 #islem bilgileri sorgulanirken guncellenecek
satin_alinan_price = 0.0

def acik_islemler_icerisinde_mi():
	global alinan_miktar
	global satin_alinan_price
	time.sleep(1)
	hedef_islem_id_bulundu_mu = False
	try:		
		islemler = exchange.fetchOpenOrders(pair) #son_islem = islemler[-1]
		for islem in islemler:
			islem_id = islem["id"]
			if (order_id == islem_id):
				hedef_islem_id_bulundu_mu = True
				alinan_miktar = islem["amount"]
				satin_alinan_price = islem["price"]
				print("islem_id: " + str(islem_id))
				print("amount: " + str(alinan_miktar))
				print("price: " + str(satin_alinan_price))
	except Exception as e:
		print("error 4567: " + str(e))
		hedef_islem_id_bulundu_mu = False
		
	return hedef_islem_id_bulundu_mu
	
def tamamlanmis_islemler_icerisinde_mi():
	time.sleep(1)
	global alinan_miktar
	global satin_alinan_price
	hedef_islem_id_bulundu_mu = False
	try:
		islemler = exchange.fetchClosedOrders(pair) #son_islem = islemler[-1]
		for islem in islemler:
			islem_id = islem["id"]
			if (order_id == islem_id):
				hedef_islem_id_bulundu_mu = True
				alinan_miktar = islem["amount"]
				satin_alinan_price = islem["price"]
				print("islem_id: " + str(islem_id))
				print("amount: " + str(alinan_miktar))
				print("price: " + str(satin_alinan_price))
	except Exception as e:
		print("error 4568: " + str(e))
		hedef_islem_id_bulundu_mu = False		
		
	return hedef_islem_id_bulundu_mu
		
def islem_durumu_ne():
	if tamamlanmis_islemler_icerisinde_mi():
		return "tamamlanmis"
	elif acik_islemler_icerisinde_mi():
		return "acik"
	else:
		return "boyle bir islem yok"
		
def oncelikle_islemi_dogrula():	
	islem_durumu = ""
	while islem_durumu != "tamamlanmis":
		islem_durumu = islem_durumu_ne()
		print("islem durumu: " + islem_durumu)
		
	#satin alma isleminin tamamlandigi onaylandi
	while True:
		#elden cikarana kadar mokoko :)
		satis_stratejisi()
		time.sleep(1)
	
	
satis_stratejisi_kontrol_sayisi=0
def satis_stratejisi():
	global satis_stratejisi_kontrol_sayisi
	satis_stratejisi_kontrol_sayisi += 1
	son_price = fiyat_ogren(pair,"satis")
	
	ekrani_temizle()

	print("")
	print(pair + " fiyat")
	print("==================================")
	print("Alinan : " + format(satin_alinan_price, '.8f'))
	print("Guncel : " + format(son_price, '.8f'))
	
	print("")
	print("Kazanc")
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
	print("Kontrol Sayisi")
	print("==================================")
	print(str(satis_stratejisi_kontrol_sayisi))
	
	print("")
	kazanc_yuzdesi = float(kazanc_yuzdesi)
	if (kazanc_yuzdesi <= stop_loss):
		print("zarar yaziyor cikiyorum")
		satis_yap()
	elif (kazanc_yuzdesi >= take_profit):
		print("take profitip cikiyorum")
		satis_yap()
	else:
		take_profit_belirtildi_mi = take_profit != 9999
		stop_loss_belirtildi_mi = stop_loss != -9999
		if take_profit_belirtildi_mi or stop_loss_belirtildi_mi:
			print("Strateji")
			print("====================")
			if take_profit_belirtildi_mi:
				print("take profit: %" + str(take_profit))
			if stop_loss_belirtildi_mi:
				print("stop loss: %" + str(stop_loss))
				
				
def satis_yap():
	global alinan_miktar
	satilacak_miktar = alinan_miktar
	komisyon_tutari = satilacak_miktar * 0.1 / 100 #okex %0.1'lik komisyon aliyor
	satilacak_miktar = satilacak_miktar - komisyon_tutari

	print("Satis emri giriyorum..")
	print("===================================")
	print("satilacak_miktar: " + str(satilacak_miktar))
	
	real_pair_price = float(fiyat_ogren(pair, "alis"))
	print("real_pair_price: " + str(real_pair_price))

	satis_garanti_olsun_diye_yuzde_kac_dusuruyorum = 0.01
	real_pair_price = real_pair_price - (real_pair_price * satis_garanti_olsun_diye_yuzde_kac_dusuruyorum / 100)

	print("satis_garanti_olsun_diye_yuzde_kac_dusuruyorum: %" + str(satis_garanti_olsun_diye_yuzde_kac_dusuruyorum))
	print("benim satacagim fiyat: " + str(real_pair_price))
	
	satis_emri = exchange.create_order(pair, "limit" , "sell", satilacak_miktar, real_pair_price)
	print(satis_emri)
	input("islem tamamlandi..")

def fiyat_ogren(pair,side="alis"):
	ask_bid = ""
	if side=="alis": ask_bid="bid"  #yesil buy bid
	if side=="satis": ask_bid="ask" #kirmizi sell ask
	return float(exchange.fetch_ticker(pair)[ask_bid])
	
def basla():
	print("kontrol ediyorum..")
	oncelikle_islemi_dogrula()
				
if __name__ == '__main__':	
	basla()
	