# -*- coding: utf-8 -*-
import ccxt, os, time, datetime, sys, requests
sys.path.append("py")
from fonksiyonlar import *
os.chdir(basladigim_yer) #calisma klasorunu mevcut klasor olarak degistiriyorum
import signali_cek_listings
basligi_degistir() #powershell ile cagrilirsam bunu sil

#============= internet varsa devam ediyorum
while True:	
	if internet_var_mi():
		break
	else:
		print("internet baglantisi bekleniyor..")
		time.sleep(1)
		
target_altcoin = ""
haber_turu = ""
tespit_edilme_zamani = ""
iletilecek = ""

def basla():
	global target_altcoin, haber_turu, tespit_edilme_zamani, iletilecek
	print("starting the controls")

	target_altcoin = signali_cek_listings.basla()
	haber_turu = signali_cek_listings.haber_turu.upper()
	signaldeki_coin_hangi_exchange_sitelerinde_bulundu = signali_cek_listings.signaldeki_coin_hangi_exchange_sitelerinde_bulundu
		
	if target_altcoin:
		#target_altcoin belirlendiyse
		target_altcoin.upper()
	else:
		#bir sekilde hata meydana geldiyse
		print(dosya_adim() + ": target_altcoin bana tam olarak ulasmadi")
		programi_yeniden_ac()
	
	#alis emri giriyorum
	alinabilecek_exchange_siteleri = ["binance", "okex"]
	
	for exchange_sitesi in alinabilecek_exchange_siteleri:
		if exchange_sitesi in signaldeki_coin_hangi_exchange_sitelerinde_bulundu:
			if exchange_sitesi == "binance":
				if haber_turu.upper() == "WILL LIST" or haber_turu.upper() == "LISTS":
					buy_with_binancemiyorum_uyarisi = haber_turu + " haber turunde ani dususler olabildigi icin binance ile almiyorum"
					iletilecek += "(" + buy_with_binancemiyorum_uyarisi + ")";
					print(buy_with_binancemiyorum_uyarisi)
				else:
					su_exchange_ile_al(exchange_sitesi)
			else:
				su_exchange_ile_al(exchange_sitesi)
			
	#kullaniciya haber veriyorum
	tespit_edilme_zamani = signali_cek_listings.tespit_edilme_zamani
	iletilecek = "Binance " + haber_turu + " ($" + target_altcoin + ")" + " " + "(" + str(tespit_edilme_zamani) + ")" + " alındı => " + str(signaldeki_coin_hangi_exchange_sitelerinde_bulundu) + " " + iletilecek
	
	print("iletilecek: " + iletilecek)
	ilet(iletilecek)

	bekle(60)
	programi_yeniden_ac()
	
def su_exchange_ile_al(exchange):
	global iletilecek
	trade_config = {
			"take_profit" : "10",
			"stop_loss" : "-5",
			"haber_turu": haber_turu,
			"target_altcoin": target_altcoin
	}
	if haber_turu == "ADDS": trade_config["take_profit"] = "5"
	if haber_turu == "LISTS" or haber_turu == "WILL LIST": trade_config["take_profit"] = "20"
	if haber_turu == "GIVEAWAYS": trade_config["take_profit"] = "10"
	dosya = exchange + "_ile_al.json"
	dosya_tam_adres = log_klasoru + "/" + dosya
	if not os.path.exists(dosya_tam_adres):
		dosyaya_yaz(dosya_tam_adres, trade_config)
		print("trade config " + dosya + " dosyasina yazildi.")
		#iletilecek += " " + "(" + "=>" + dosya + ")"

if __name__ == "__main__":
	basla()



