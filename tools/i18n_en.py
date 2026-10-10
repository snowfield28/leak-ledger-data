"""英語版ページ用の対応表。日本語のラベル（data.json の分類名）を英語表示に置き換える。

事案ごとの文章（概要・調査の状況・対応など）は翻訳しない。公式発表の日本語のまま載せる。
新しい分類名が data.json に増えたら、ここに足す（足りないときは日本語のまま表示される）。
"""

IND = {
    "小売・EC": "Retail & e-commerce", "飲食": "Food service", "金融・保険": "Finance & insurance",
    "通信・IT": "Telecom & IT", "メディア・出版": "Media & publishing", "運輸・交通": "Transport",
    "製造": "Manufacturing", "建設・不動産": "Construction & real estate", "エネルギー": "Energy",
    "生活サービス・レジャー": "Consumer services & leisure", "医療・製薬": "Healthcare & pharma",
    "人材・教育・業務支援": "HR, education & business services", "公共機関": "Public sector",
    "大学・学校": "Universities & schools", "病院・医療": "Hospitals & clinics", "団体": "Associations & nonprofits",
}
TYPE = {
    "不正アクセス": "Unauthorized access", "委託先経由": "Via contractor", "ランサムウェア": "Ransomware",
    "誤送信・誤掲載": "Misdelivery / mis-posting", "紛失・盗難": "Loss / theft",
    "設定ミス・不具合": "Misconfiguration / bug", "内部不正": "Insider misconduct",
}
CAUSE = {
    "cyber": "Cyber attack", "loss": "Loss / theft", "mis": "Misdelivery / mis-posting",
    "insider": "Insider misconduct", "config": "Misconfiguration / bug",
}
ITEM = {
    "name": "Name", "addr": "Address", "tel": "Phone number", "mail": "Email address", "birth": "Date of birth",
    "work": "Employer", "deal": "Contract / purchase records", "acct": "Bank account", "card": "Credit card",
    "id": "ID / password", "doc": "ID document",
}
WHO = {
    "cust": "Customers / users", "biz": "Business partners / corporate clients", "staff": "Employees / staff",
    "work": "Business information (not personal data)", "unk": "Not specified",
}
STATUS = {"closed": "Investigation complete", "ongoing": "Under investigation / awaiting updates"}
STATUS_SHORT = {"closed": "Closed", "ongoing": "Ongoing"}
MONTHS = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def edate(s):
    y, m, d = s.split("-")
    return f"{MONTHS[int(m)]} {int(d)}, {int(y)}"


def eym(s):
    y, m, _ = s.split("-")
    return f"{MONTHS[int(m)]} {int(y)}"


def enum(n):
    """件数を K / M / B で短く表す。"""
    if n is None:
        return "—"
    for v, u in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if n >= v:
            x = round(n / v, 1)
            return (f"{x:.1f}".rstrip("0").rstrip(".")) + u
    return f"{int(n):,}"
