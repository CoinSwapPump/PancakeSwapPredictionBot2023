import ccxt
import os
import sys
sys.path.append("py")
import time
import datetime
from fonksiyonlar import *
os.chdir(basladigim_yer) #calisma klasorunu mevcut klasor olarak degistiriyorum

basligi_degistir() #powershell ile cagrilirsam bunu sil
target_altcoin=""
pair=""

#------ config
config = ayarlari_config_json_dosyasindan_oku()
k_sifreli = config['buy_with_binance']['api_key']
s_sifreli = config['buy_with_binance']['api_secret']
target_coin = config['buy_with_binance']['target_coin']
use_balance = config['buy_with_binance']['use_balance'] #target_coin ile
trade_with_real_account = str_to_bool(config['buy_with_binance']['trade_with_real_account'])
#------ config

k = sifre_coz(k_sifreli)
s = sifre_coz(s_sifreli)

exchange = ccxt.binance({
	'apiKey': k,
	'secret': s,
	'enableRateLimit': True,
	'options': { 'adjustForTimeDifference': True }	
})

print("Caching the exchange settings....")
#market bilgilerini cacheliyorum ki ccxt daha hizli olsun
exchange.load_markets()
#tickerlar'i en bastan cacheliyorum ki sonradan kontrolu hizli olsun
tickerlar = exchange.fetch_tickers()

#kar_hesaplama
take_profit = ""
stop_loss = ""

os.system('cls')

def basla():
	global target_altcoin, use_balance, pair
	
	if ("%" in str(use_balance)):
		target_coin_bakiyem = bakiye_hesapla(target_coin)
		yuzde = float(str(use_balance).replace("%",""))
		use_balance = yuzde / 100 * bakiye_hesapla(target_coin)

	if not target_altcoin or target_altcoin == "":
		if len(sys.argv) > 1:
			#parametre ile mi gelmis onu kontrol ediyorum
			target_altcoin=sys.argv[1] #1. parametre orn: LTC
			if target_altcoin == "i_couldnt_buy_new_altcoin_buy_it_yourself":
				print("i_couldnt_buy_new_altcoin_buy_it_yourself")
				target_altcoin = input("Type the altcoin to buy..")
			else:
				print("target_altcoin " + " listings.py dosyasiyla gonderildi: " + target_altcoin)
		else:
			print("coin manuel girilecek")
			target_altcoin = input("Type the altcoin to buy..")
	else:
		print("target_altcoin daha onceden belirlenmis")
		
	print("target_altcoin: " + str(target_altcoin))
	if (not target_altcoin):
		print("target_altcoin null cikti")
		basla()
	else:
		print("target_altcoin > " + target_altcoin)

	pair = (target_altcoin + "/" + target_coin).upper()
	print("pair: " + pair)
	
	timestamp_islem_baslangici = time.time()
	
	real_pair_price = float(ticker_fiyati_ogren(pair))

	print(pair + ' real_pair_price: ' + str(real_pair_price))
	
	#quantity'i hesapliyorum
	quantity = use_balance/real_pair_price
	print ("use_balance: " + str(use_balance))
	print ("quantity: " + str(quantity) + target_altcoin)

	if (trade_with_real_account):
		#alis emri giriyorum
		print ("alis emri giriliyor..")
		alis_emri = exchange.create_market_buy_order(pair, quantity)
	else:
		#placing test order
		print("placing test order...")
		params = {'test': True,}
		alis_emri = exchange.create_order(pair, "market" , "buy", quantity, real_pair_price, params)
		
	#bilgileri ekrana yazdir
	print (alis_emri)
	timestamp_islem_bitisi = time.time()
	alis_emri_kac_saniyede_girildi = float(format(timestamp_islem_bitisi - timestamp_islem_baslangici, '.2f'))
	print ("=======================")
	print ("timestamp: " + str(timestamp_islem_bitisi))
	print ("time: " + str(full_tarih(timestamp_islem_bitisi)))
	print ("bought in: " + str(alis_emri_kac_saniyede_girildi) + " sn")
	print ("=======================")
	
	logla("alis islemi tamamlandi")
	
	print("")
	print("kar hesaplama dosyasini aciyorum")
	dosya = basladigim_yer + '\\py\\binance_profit_tracker.py'
	komut = 'start cmd @cmd /k ' + dosya + ' ' + target_altcoin + ' ' + str(real_pair_price) + ' ' + take_profit + ' ' + stop_loss
	
	print(komut)
	os.system(komut)
	
	bekle(20)
	programi_yeniden_ac()
	
def bakiye_hesapla(coin):
	try: return exchange.fetch_balance()[coin.upper()]['free']
	except: return 0
	
def ticker_fiyati_ogren(ticker):
	tickerlar_klasoru = basladigim_yer + "\\py\\tickerlar"
	dosya_full_adres = tickerlar_klasoru + "\\" + ticker.replace("/","") + ".txt"
	
	fiyat = ""
	
	try:
		#oncelikle ticker dosyasindan cekiyorum
		with open(dosya_full_adres,'r') as f:
			fiyat = f.read()
		print("altcoin price read from local file")
	except Exception as e:
		print(str(e))
		#bulamazsam api ile ogreniyorum
		fiyat = float(exchange.fetch_ticker(ticker)['bid'])
		print("altcoin price calculated with api request")
		
	return fiyat	

def txt_dosyasindan_islem_yapilacak_altcoini_cek():
	global target_altcoin, take_profit, stop_loss
	dosya = log_klasoru + "/" + dosya_adim().replace(".py",".json")
	
	kontrol_sayisi = 0
	while True:
		try:
			kontrol_sayisi += 1
			if kontrol_sayisi % 1000 == 1: restart_zamanlarindaysam_programi_yeniden_ac()
			dosya_mevcut_mu = os.path.exists(dosya)
			os.system('cls')
			print("")
			print(dosya_adim())
			print("=======================")
			print("controlled: " + str(kontrol_sayisi))
			print(dosya + " exists? " + str(dosya_mevcut_mu))
			if dosya_mevcut_mu:
				son_modification_time = os.path.getmtime(dosya)
				son_modification_uzerinden_gecen_saniye = int(time.time() - son_modification_time)
				satin_alinabilir_mi = son_modification_uzerinden_gecen_saniye <= 10
				
				print(str(son_modification_uzerinden_gecen_saniye) + "seconds passed over last overwrite")
				print("should i buy? " + str(satin_alinabilir_mi))
				
				if satin_alinabilir_mi:
					trade_config = json_dosyasi_oku(dosya)					
					target_altcoin = trade_config['target_altcoin'].upper()
					take_profit = trade_config['take_profit']
					stop_loss = trade_config['stop_loss']
					if target_altcoin != False:
						break
				else:
					if son_modification_uzerinden_gecen_saniye >= 10 * 60:
						dosyayi_arsivle(dosya)
						
		except Exception as e:
			print("error 4546: " + str(e))
		
	#while dongusu gecildiyse target_altcoin bulundu demektir
	print("")
	print("trade config")
	print("=================")
	print(trade_config)
	
	
if __name__ == "__main__":
	txt_dosyasindan_islem_yapilacak_altcoini_cek() #fonksiyonlar.py
	basla()
	



