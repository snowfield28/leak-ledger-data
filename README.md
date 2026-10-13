# 国内サイバー被害企業台帳

サイバー攻撃（ランサムウェア・不正アクセス・委託先経由）で個人情報の漏えい、または漏えいの可能性を公表した国内企業の事案をまとめたデータです。

- `data.json`：事案データ。Web版とiPhoneアプリの両方がこのファイルを読み込みます。
- `index.html`：Web版の台帳（GitHub Pagesで公開）。

## データについて

- 件数・状況・流出した情報は、各社の公表を報じた記事で確認した内容です。各事案に情報源のリンクがあります。
- `st` が `c` は漏えいを確認、`p` は漏えいの可能性を公表した事案です。
- `auto: true` の事案は自動収集で追加され、まだ人が確認していないものです。
- 件数は続報で変わることがあります。最新の状況は各社の公表資料で確認してください。犯行声明は攻撃者側の主張で、事実と確定したものではありません。

## 更新の仕組み（自動取り込み）

1. **収集（GitHub Actions、毎日）** `tools/collect.py`
   `tools/sources.json` の一覧ページから新着の漏えい報道を集め、記事にある公式発表らしいリンクをたどって本文（HTML・PDF）を取得し、
   `inbox.json` と `inbox/texts/*.txt` に保存します。robots.txt で拒否されたもの、本文が短いもの（画像・JavaScript描画）は `status` で区別します。
2. **判断（定期実行のClaude）** `inbox.json` を読み、保存済みの本文だけで照合して、パッチJSONを作ります。
   既存の保留・対象外の再確認もここで行います。
3. **反映** `python3 tools/apply.py patch.json`
   パッチを3つのJSONに反映し、`tools/validate.py` で検証し、通れば `tools/build_pages.py` で個別ページを作り直します。検証に失敗すれば元に戻ります。
   パッチの `inbox_done` に処理した記事URLを入れると `inbox.json` から外れます。
4. **手動の貼り付け** 自動で開けない公式発表は `manual/` に貼ります（`manual/README.md`）。

## 検証

`python3 tools/validate.py` — 重複ID、スキーマ、announced/occurred/date の整合、pendingCount を調べます。
