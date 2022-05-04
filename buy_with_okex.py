import ccxt
import os
import sys
sys.path.append("py")
import re
import time
import datetime
from fonksiyonlar import *
os.chdir(basladigim_yer) #calisma klasorunu mevcut klasor olarak degistiriyorum

basligi_degistir() #powershell ile cagrilirsam bunu sil
target_altcoin=""
pair=""

#configi dosyadan oku
config = ayarlari_config_json_dosyasindan_oku()

#okunan dosyadan configi serpistir
k_sifreli = config['buy_with_okex']['api_key']
s_sifreli = config['buy_with_okex']['api_secret']
target_coin = config['buy_with_okex']['target_coin']
use_balance = config['buy_with_okex']['use_balance'] #target_coin ile
trade_with_real_account = str_to_bool(config['buy_with_okex']['trade_with_real_account'])

k = sifre_coz(k_sifreli)
s = sifre_coz(s_sifreli)
exchange = ccxt.okex({
	'apiKey': k,
	'secret': s,
	'enableRateLimit': True,
	'options': {'adjustForTimeDifference': True}	
})

print("Caching the exchange settings....")
#market bilgilerini cacheliyorum ki ccxt daha hizli olsun
exchange.load_markets()
#tickerlar'i en bastan cacheliyorum ki sonradan kontrolu hizli olsun
tickerlar = exchange.fetch_tickers()

#kar_hesaplama
take_profit = ""
stop_loss = ""

order_id = 0
		
def basla():
	global order_id, target_altcoin, use_balance, pair
	
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
		
	pair = (target_altcoin + "/" + target_coin).upper()
	print("pair: " + pair)
	real_pair_price = float(fiyat_ogren(pair, "satis"))
	print("normal satis fiyati: " +  str(notation_temizle(real_pair_price)))
	alis_garanti_olsun_diye_yuzde_kac_ekliyorum = 0.02
	real_pair_price = real_pair_price + (real_pair_price * alis_garanti_olsun_diye_yuzde_kac_ekliyorum / 100)
	print("alis_garanti_olsun_diye_yuzde_kac_ekliyorum: %" + str(alis_garanti_olsun_diye_yuzde_kac_ekliyorum))
	print("benim alacagim fiyat: " +  str(notation_temizle(real_pair_price)))
	
	if ("%" in str(use_balance)):
		#config.json dosyasinda use_balance yuzde ile belirtilmis o yuzden tam olarak hesaplamaya calisiyorum
		yuzde = float(str(use_balance).replace("%",""))
		
		bakiyem = bakiye_hesapla(target_coin)
		use_balance = yuzde / 100 * bakiyem
		
		print("")
		print("toplam: " + str(bakiyem) + target_coin)
		print("islem yapilacak: " + str(use_balance) + target_coin + "(" + "bakiyeye orani: %" + str(yuzde) + ")")
		
	#quantity'i hesapliyorum
	quantity = use_balance/real_pair_price
	
	if trade_with_real_account == False:
		#test emri icin bilgileri yeniden duzeltiyorum
		use_balance = 10 / 100 * bakiyem
		test_emri_icin_fiyati_yuzde_kac_indiriyorum = 50
		real_pair_price = real_pair_price - (real_pair_price * test_emri_icin_fiyati_yuzde_kac_indiriyorum / 100)
		print("placing test order yalniz bu emri siteden silmeyi unutma")
		
	print("")
	print("Alis emri giriyorum..")
	print("===================================")
	print("quantity: " + str(quantity))
	print("use_balance: " + str(use_balance) + target_coin)
	print("alinacak fiyat: " + str(notation_temizle(real_pair_price)))
	
	try:
		alis_emri = exchange.create_order(pair, "limit" , "buy", quantity, real_pair_price)
		print(alis_emri)
		order_id = alis_emri["id"]
		print("alis emri basariyla girildi kar hesaplama dosyasini aciyorum")
	except Exception as e:
		input("alis emri girilemedi\nhata 7709: " + str(e))
				
	logla("islem tamamlandi")
	
	print("")
	print("kar hesaplama dosyasini aciyorum")
	dosya = basladigim_yer + '\\py\\okex_profit_tracker.py'
	komut = 'start cmd @cmd /k ' + dosya + ' ' + target_altcoin + ' ' + order_id + ' ' + take_profit + ' ' + stop_loss
	
	print(komut)
	os.system(komut)
	
	bekle(20)
	programi_yeniden_ac()
	
def fiyat_ogren(pair,side="alis"):
	ask_bid = ""
	if side=="alis": ask_bid="bid"  #yesil buy bid
	if side=="satis": ask_bid="ask" #kirmizi sell ask
	return float(exchange.fetch_ticker(pair)[ask_bid])
	
def bakiye_hesapla(coin):
	try: return exchange.fetch_balance()[coin.upper()]['free']
	except: return 0
	
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



