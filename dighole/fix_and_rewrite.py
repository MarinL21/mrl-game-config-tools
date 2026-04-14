import json
import subprocess

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = "11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY"
STAGING_SHEET = "AI翻译暂存"

# New header: no ID_int, 21 columns (A-U)
STAGING_HEADER = [
    "✅提交", "目标页签",
    "ID", "cn", "en", "fr", "de", "po", "zh",
    "id", "th", "sp", "ru", "tr", "vi", "it", "pl", "ar", "jp", "kr", "cns"
]

# Data: target_tab, ID, translations (no ID_int)
ROWS = [
    ["EVENT","event_cool_treasure_title","清凉探宝会","COOL TREASURE HUNT","CHASSE AU TRÉSOR","COOLE SCHATZSUCHE","CAÇA AO TESOURO","清涼探寶會","BERBURU HARTA KARUN","ล่าสมบัติสุดคูล","BÚSQUEDA DEL TESORO","ОХОТА ЗА СОКРОВИЩАМИ","HAZİNE AVI","SĂN KHO BÁU","CACCIA AL TESORO","POLOWANIE NA SKARBY","البحث عن الكنز","トレジャーハント","보물찾기","清凉探宝会"],
    ["EVENT","event_cool_treasure_label","清凉探宝会","COOL TREASURE HUNT","CHASSE AU TRÉSOR","COOLE SCHATZSUCHE","CAÇA AO TESOURO","清涼探寶會","BERBURU HARTA KARUN","ล่าสมบัติสุดคูล","BÚSQUEDA DEL TESORO","ОХОТА ЗА СОКРОВИЩАМИ","HAZİNE AVI","SĂN KHO BÁU","CACCIA AL TESORO","POLOWANIE NA SKARBY","البحث عن الكنز","トレジャーハント","보물찾기","清凉探宝会"],
    ["EVENT","event_eliminate_method","消除方式","ELIMINATION METHOD","MÉTHODE D'ÉLIMINATION","BESEITIGUNGSMETHODE","MÉTODO DE ELIMINAÇÃO","消除方式","METODE ELIMINASI","วิธีการกำจัด","MÉTODO DE ELIMINACIÓN","СПОСОБ УСТРАНЕНИЯ","ELEMİNASYON YÖNTEMİ","PHƯƠNG PHÁP LOẠI BỎ","METODO DI ELIMINAZIONE","METODA ELIMINACJI","طريقة الإزالة","消去方法","제거 방법","消除方式"],
    ["EVENT","event_tool_catch_all","一网打尽","CATCH ALL","ATTRAPER TOUT","ALLES FANGEN","PEGAR TUDO","一網打盡","TANGKAP SEMUA","จับทั้งหมด","ATRAPAR TODO","ПОЙМАТЬ ВСЁ","HEPSİNİ YAKALA","BẮT HẾT","CATTURA TUTTO","ZŁAP WSZYSTKO","اصطاد الجميع","一網打尽","모두 잡기","一网打尽"],
    ["EVENT","event_tool_freeze","冻结一片","FREEZE AREA","GELER UNE ZONE","BEREICH EINFRIEREN","CONGELAR ÁREA","凍結一片","BEKUKAN AREA","แช่แข็งพื้นที่","CONGELAR ÁREA","ЗАМОРОЗИТЬ ОБЛАСТЬ","BÖLGE DONDUR","ĐÓNG BĂNG KHU VỰC","CONGELA AREA","ZAMROŹ OBSZAR","تجميد المنطقة","エリア凍結","구역 동결","冻结一片"],
    ["EVENT","event_tool_line_view","一线风景","LINE VIEW","VUE EN LIGNE","LINIENANSICHT","VISÃO DE LINHA","一線風景","PEMANDANGAN GARIS","มุมมองเส้น","VISTA DE LÍNEA","ЛИНЕЙНЫЙ ОБЗОР","SATIR GÖRÜNÜMÜ","NHÌN THEO HÀNG","VISTA A LINEA","WIDOK LINIOWY","عرض الخط","ラインビュー","라인 뷰","一线风景"],
    ["EVENT","event_tool_blind_flip","精准盲翻","PRECISE FLIP","RETOURNEMENT PRÉCIS","PRÄZISES AUFDECKEN","VIRADA PRECISA","精準盲翻","BALIK PRESISI","พลิกแม่นยำ","VOLTEO PRECISO","ТОЧНЫЙ ПЕРЕВОРОТ","KESİN ÇEVİRME","LẬT CHÍNH XÁC","CAPOVOLGIMENTO PRECISO","PRECYZYJNE ODKRYCIE","قلب دقيق","正確フリップ","정밀 뒤집기","精准盲翻"],
    ["EVENT","event_flip_cost","点击翻板，消耗一个{0}","Flip a tile. Costs 1 {0}.","Retournez une tuile. Coûte 1 {0}.","Decke ein Feld auf. Kostet 1 {0}.","Vire uma peça. Custa 1 {0}.","點擊翻板，消耗一個{0}","Balik ubin. Biaya 1 {0}.","พลิกแผ่น ใช้ {0} 1 ชิ้น","Voltea una ficha. Cuesta 1 {0}.","Переверните плитку. Стоимость: 1 {0}.","Bir karo çevir. 1 {0} harcar.","Lật ô. Tốn 1 {0}.","Gira una tessera. Costa 1 {0}.","Odwróć kafelek. Kosztuje 1 {0}.","اقلب بلاطة. يكلف 1 {0}.","タイルをめくる。{0}を1個消費。","타일을 뒤집습니다. {0} 1개를 소모합니다.","点击翻板，消耗一个{0}"],
    ["EVENT","event_exchange_shop","兑换商店","EXCHANGE SHOP","BOUTIQUE D'ÉCHANGE","TAUSCHGESCHÄFT","LOJA DE TROCA","兌換商店","TOKO PENUKARAN","ร้านแลกเปลี่ยน","TIENDA DE INTERCAMBIO","МАГАЗИН ОБМЕНА","TAKAS MAĞAZASI","CỬA HÀNG ĐỔI THƯỞNG","NEGOZIO DI SCAMBIO","SKLEP WYMIANY","متجر الاستبدال","交換ショップ","교환 상점","兑换商店"],
    ["EVENT","event_achievement_pack","成就礼包","ACHIEVEMENT PACK","PACK SUCCÈS","ERFOLGSPAKET","PACOTE DE CONQUISTA","成就禮包","PAKET PENCAPAIAN","แพ็คความสำเร็จ","PAQUETE DE LOGRO","НАБОР ДОСТИЖЕНИЙ","BAŞARI PAKETİ","GÓI THÀNH TÍCH","PACCHETTO RISULTATI","PAKIET OSIĄGNIĘĆ","حزمة الإنجاز","アチーブメントパック","업적 팩","成就礼包"],
    ["EVENT","event_decoration_gift","装饰好礼","DECORATION GIFT","CADEAU DÉCO","DEKORATIONSGESCHENK","PRESENTE DECORATIVO","裝飾好禮","HADIAH DEKORASI","ของขวัญตกแต่ง","REGALO DECORATIVO","ПОДАРОК-УКРАШЕНИЕ","DEKORASYON HEDİYESİ","QUÀ TRANG TRÍ","REGALO DECORATIVO","PREZENT DEKORACYJNY","هدية الديكور","デコレーションギフト","장식 선물","装饰好礼"],
    ["EVENT","event_collected_rewards","已收集奖励：{0}/{1}","Collected Rewards: {0}/{1}","Récompenses collectées: {0}/{1}","Gesammelte Belohnungen: {0}/{1}","Recompensas coletadas: {0}/{1}","已收集獎勵：{0}/{1}","Hadiah Terkumpul: {0}/{1}","รางวัลที่สะสม: {0}/{1}","Recompensas obtenidas: {0}/{1}","Собрано наград: {0}/{1}","Toplanan Ödüller: {0}/{1}","Phần thưởng đã thu thập: {0}/{1}","Ricompense raccolte: {0}/{1}","Zebrane nagrody: {0}/{1}","المكافآت المجمعة: {0}/{1}","獲得済み報酬：{0}/{1}","수집한 보상: {0}/{1}","已收集奖励：{0}/{1}"],
    ["EVENT","event_collect_all_chest","集齐所有奖励可开启宝箱","Collect all rewards to open the treasure chest","Collectez toutes les récompenses pour ouvrir le coffre","Sammle alle Belohnungen, um die Schatztruhe zu öffnen","Colete todas as recompensas para abrir o baú","集齊所有獎勵可開啟寶箱","Kumpulkan semua hadiah untuk membuka peti harta","สะสมรางวัลครบเพื่อเปิดหีบสมบัติ","Recoge todas las recompensas para abrir el cofre","Соберите все награды, чтобы открыть сундук","Hazine sandığını açmak için tüm ödülleri topla","Thu thập tất cả phần thưởng để mở rương kho báu","Raccogli tutte le ricompense per aprire lo scrigno","Zbierz wszystkie nagrody, aby otworzyć skrzynię","اجمع كل المكافآت لفتح صندوق الكنز","すべての報酬を集めて宝箱を開けよう","모든 보상을 모아 보물 상자를 열 수 있습니다","集齐所有奖励可开启宝箱"],
    ["EVENT","event_hot_events","热门活动","HOT EVENTS","ÉVÉNEMENTS POPULAIRES","BELIEBTE EVENTS","EVENTOS POPULARES","熱門活動","ACARA POPULER","กิจกรรมยอดฮิต","EVENTOS POPULARES","ГОРЯЧИЕ СОБЫТИЯ","POPÜLER ETKİNLİKLER","SỰ KIỆN HOT","EVENTI POPOLARI","POPULARNE WYDARZENIA","الأحداث الساخنة","人気イベント","인기 이벤트","热门活动"],
    ["EVENT","event_normal_events","普通活动","EVENTS","ÉVÉNEMENTS","EVENTS","EVENTOS","普通活動","ACARA","กิจกรรม","EVENTOS","СОБЫТИЯ","ETKİNLİKLER","SỰ KIỆN","EVENTI","WYDARZENIA","الأحداث","イベント","이벤트","普通活动"],
    ["EVENT","event_tournament","赛事","TOURNAMENT","TOURNOI","TURNIER","TORNEIO","賽事","TURNAMEN","ทัวร์นาเมนต์","TORNEO","ТУРНИР","TURNUVA","GIẢI ĐẤU","TORNEO","TURNIEJ","البطولة","トーナメント","토너먼트","赛事"],
    ["EVENT","event_selected_tab","选中页签","SELECTED","SÉLECTIONNÉ","AUSGEWÄHLT","SELECIONADO","選中頁簽","DIPILIH","เลือกแล้ว","SELECCIONADO","ВЫБРАНО","SEÇİLDİ","ĐÃ CHỌN","SELEZIONATO","WYBRANO","محدد","選択中","선택됨","选中页签"],
]


def get_credentials():
    result = subprocess.run(
        ["gws", "auth", "export", "--unmasked"],
        capture_output=True, text=True, encoding="utf-8",
        shell=True,
    )
    creds_data = json.loads(result.stdout.strip())
    return Credentials(
        token=None,
        refresh_token=creds_data["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )


def main():
    credentials = get_credentials()
    service = build("sheets", "v4", credentials=credentials)
    sheets_api = service.spreadsheets()

    # Get staging sheet ID
    spreadsheet = sheets_api.get(
        spreadsheetId=SPREADSHEET_ID,
        fields="sheets.properties"
    ).execute()
    staging_sheet_id = None
    for s in spreadsheet["sheets"]:
        if s["properties"]["title"] == STAGING_SHEET:
            staging_sheet_id = s["properties"]["sheetId"]
            break

    print(f"[1] staging sheetId={staging_sheet_id}")

    # Clear everything (header + data)
    sheets_api.batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"requests": [{
            "updateCells": {
                "range": {"sheetId": staging_sheet_id, "startRowIndex": 0},
                "fields": "userEnteredValue,dataValidation,userEnteredFormat",
            }
        }]},
    ).execute()
    print("[2] cleared entire staging sheet")

    # Write new header (21 columns, A-U)
    sheets_api.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{STAGING_SHEET}'!A1:U1",
        valueInputOption="RAW",
        body={"values": [STAGING_HEADER]},
    ).execute()

    # Format header
    sheets_api.batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"requests": [{
            "repeatCell": {
                "range": {
                    "sheetId": staging_sheet_id,
                    "startRowIndex": 0, "endRowIndex": 1,
                    "startColumnIndex": 0, "endColumnIndex": len(STAGING_HEADER),
                },
                "cell": {
                    "userEnteredFormat": {
                        "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
                        "backgroundColor": {"red": 0.29, "green": 0.53, "blue": 0.78},
                    }
                },
                "fields": "userEnteredFormat",
            }
        }]},
    ).execute()
    print("[3] wrote new header (21 columns, no ID_int)")

    # Write data to B2:U (skip A for checkboxes)
    end_row = 1 + len(ROWS)
    sheets_api.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{STAGING_SHEET}'!B2:U{end_row}",
        valueInputOption="RAW",
        body={"values": ROWS},
    ).execute()
    print(f"[4] wrote {len(ROWS)} rows (B2:U{end_row})")

    # Set checkboxes + dropdown
    sheets_api.batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"requests": [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": staging_sheet_id,
                        "startRowIndex": 1, "endRowIndex": end_row,
                        "startColumnIndex": 0, "endColumnIndex": 1,
                    },
                    "cell": {
                        "dataValidation": {"condition": {"type": "BOOLEAN"}, "strict": True},
                        "userEnteredValue": {"boolValue": False},
                    },
                    "fields": "dataValidation,userEnteredValue",
                }
            },
            {
                "setDataValidation": {
                    "range": {
                        "sheetId": staging_sheet_id,
                        "startRowIndex": 1, "endRowIndex": end_row,
                        "startColumnIndex": 1, "endColumnIndex": 2,
                    },
                    "rule": {
                        "condition": {
                            "type": "ONE_OF_LIST",
                            "values": [{"userEnteredValue": v} for v in [
                                "EVENT","GENERAL","HERO","BUILDING","ITEM",
                                "QUEST","BATTLE","SHOP","MAIL","ALLIANCE",
                                "MENU","MAP","PLAYER","SOLDIER","RESEARCH",
                            ]],
                        },
                        "showCustomUi": True,
                        "strict": False,
                    },
                }
            },
        ]},
    ).execute()
    print("[5] added checkboxes + dropdown")

    # Clean up old bad rows from EVENT tab (ID_int >= 2000000000 or 1311382640+)
    result = sheets_api.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="EVENT!A:A",
    ).execute()
    all_ids = result.get("values", [])
    bad_rows = []
    for i, row in enumerate(all_ids):
        if i == 0 or not row:
            continue
        try:
            v = int(row[0])
            if v >= 1311382640:
                bad_rows.append(i + 1)
        except ValueError:
            pass

    if bad_rows:
        event_sheet_id = 550403607
        deletes = []
        for idx in sorted(bad_rows, reverse=True):
            deletes.append({
                "deleteDimension": {
                    "range": {
                        "sheetId": event_sheet_id,
                        "dimension": "ROWS",
                        "startIndex": idx - 1,
                        "endIndex": idx,
                    }
                }
            })
        sheets_api.batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={"requests": deletes},
        ).execute()
        print(f"[6] cleaned {len(bad_rows)} bad rows from EVENT")
    else:
        print("[6] no bad rows to clean from EVENT")

    print(f"\nDone! Staging has {len(ROWS)} rows, no ID_int.")
    print(f"ID_int will be auto-generated when committing via Apps Script.")


if __name__ == "__main__":
    main()
