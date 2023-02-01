# TextWallGenerator
壁文字ジェネレーター
![](https://github.com/rei05/TextWallGenerator/wiki/gif/demo.gif)

# 使い方

## 1. TextWallGeneratorのダウンロード
`TextWallGenerator.zip`を解凍し、好きな場所に置きます。

`TextWallGenerator.exe`があるのと同じ場所に`fonts`という名前のフォルダを作成します。
![](/img/folder.PNG)

## 2. フォントファイルの準備
下記のサイトで配布されているような比較的粗いドットで構成されたフォントの使用を推奨します。

- [KHドットフォントシリーズ](http://jikasei.me/font/kh-dotfont/)
- [自家製ドットフォントシリーズ](http://jikasei.me/font/jf-dotfont/)

上記のサイトではページ下の方に一括ダウンロードのリンクがあります。
![](/img/download.PNG)

使いたいフォントファイルをさっき作った`fonts`フォルダに置きます。

## 3. 環境設定
TextWallGeneratorフォルダの中の`settings.yaml`をテキストエディタで開き、環境に合わせて設定を書き換えてください。

| 項目 | 説明 |
| --- | --- |
| HJD | 譜面のHalfJumpDuration。※1 |

※1: HJDは、MMA2でNJSやオフセットの欄をクリックしたら出てきます。![](/img/HJD.PNG)

## 4. 壁文字設定
`input.csv`を開き、生成したい壁文字について設定します。
![](/img/input.PNG)

| 項目 | 説明 |
| --- | --- |
| Text | 生成したい文字列。 |
| TrackName | 文字列全体を制御するためのトラック名。 |
| StartBeatTime | 壁文字の出現(スポーン)時間(beat)。 |
| Duration | 壁文字の継続時間(beat)。 |
| Direction | 文字の方向。<br>`h`：横書き<br>`v`：縦書き |
| Font | 文字のフォント。`fonts`フォルダに置かれているフォントファイル名を指定。 |
| DotSize | フォントのドット数。※2 |
| Behavior | 壁文字の挙動。<br>`move`：通常の壁と同様に前方から後方へ流れる<br>`stop`：出現してから同じ位置に留まって動かずDuration経過後に消える |

※2: フォントのドット数はフォントファイルの名前や配布元サイトに記載されていることが多いです。使用するフォントと対応するドット数の設定を合わせることを推奨します。

![](/img/fontfile.PNG)
![](/img/dotsize1.PNG)
![](/img/dotsize2.PNG)




## 5. 壁文字を生成する
`TextWallGenerator.exe`をダブルクリックして実行します。

コンソールウィンドウが出現し、「Completed!」と表示されれば生成完了です。
![](/img/console.PNG)

新たに`generated_files`というフォルダが生成されています。

中には、TrackNameで指定した名前のdatファイルと`parentTracks.dat`というファイルが入っています。

## 6. 壁文字を譜面に組み込む
TrackNameで指定した名前のdatファイルの中身は、壁文字本体を表現する記述となっていて、譜面datファイルの`"_obstacles"`キーに対応する配列の要素がカンマ区切りで並んでいます。

テキストを全て選択してコピーし、譜面ファイルの下の図の[ ]の中に追加します。既に他の要素が記述されている場合は、カンマで区切って追加してください。![](/img/obstacles.PNG)

この状態で譜面を保存したら、一度BeatSaberのゲームを起動して譜面を再生してみましょう。

指定したbeatのタイミングで壁が出現すれば成功です。

## 7. 壁文字のアニメーション
壁文字の位置やサイズを変更したりアニメーションを加えるには、`parentTracks.dat`を使用します。

`parentTracks.dat`の中身は、壁文字に対するトラックおよび親トラックの定義となっており、`"_customEvents"`キーに対応する配列の要素がカンマ区切りで並んでいます。

テキストを全て選択してコピーし、譜面ファイルの下の図の[ ]の中に追加します。既に他の要素が記述されている場合は、カンマで区切って追加してください。![](/img/customevents.PNG)

例えば、`"aiueo_0"`というトラックは、「あいうえお」という文字列の1文字目「あ」を構成する壁に割り当てられているトラックです。同様に`"aiueo_1"`は「い」、`"aiueo_2"`は「う」が対応しています。これらのトラックに対して新たにAnimateTrackを作成すれば、一文字ずつアニメーションを加えることができます。

`"aiueo_0"`～`"aiueo_4"`を子に持つ`"aiueo"`という親トラックは
文字列全体を制御するためのトラックです。この親トラックに対して新たにAnimateTrackを作成することで、文字列の並びを崩すことなく文字列全体にアニメーションを加えることができます。
![](/img/tracks.PNG)