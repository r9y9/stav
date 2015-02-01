# STAV
--------

[VoiceConversion.jl](https://github.com/r9y9/VoiceConversion.jl) を作る前に、統計的声質変換の実験に使っていたコードです。僕のお遊び用です。信号処理バックエンドはGo、モデルの学習、変換はPythonで書いていました。`VoiceConversion.jl`のほうが色々改善されていますが、このコードも役に立つこともあるのかなぁと思いながら、とりあえずアゲてみました。

- **[Go]** Feature extraction from speech signals
- **[Go]** Parallel data generation
- **[Python]** Model training
- **[Python]** Speech paramter conversion
- **[Go]** Waveform generation


すべてをフルスクラッチで書くのは大変なので、楽をするために、信号処理のバックエンドにはSPTKとWORLDを使っています。Cで書きたくなかったので、Goでラップしたものを使っていました。

## おぼえがき

### 音声からの特徴抽出

`gostav/extact_mcep.go` を使って、wavファイルからWORLDベースのメルケプストラムを抽出します。`scripts/extract_mcep.py` を使えばOK

例. 
```bash
python  extract.py --src_dir=~/data/cmu_arctic/cmu_us_clb_arctic/wav --dst_dir=~/data/vc/clb
python  extract.py --src_dir=~/data/cmu_arctic/cmu_us_slt_arctic/wav --dst_dir=~/data/vc/slt
```

データはJSONで出力されます。フォーマットは、コード参照（おぼえてない）

### パラレルデータを作る

`gostav/align.go`を使って、DPマッチングを行います。`scripts/parallel.py`を使えばOK。

```
python parallel.py --src_dir=~/data/vc/clb --tgt_dir=~/data/vc/slt --dst_dir=~/data/vc/clb_to_slb --diff
```

`diff`とつけると、差分特徴量として、パラレルデータを保存されます（これ設計が悪い、本当は学習時に、差分特徴にするか選択出来たほうがよい。VoiceConversion.jlではそうしました）

パラレルデータもJSONで出力されます。フォーマットは、コード見てくださいおねがいします

### 変換モデル学習

GMMのみサポート

```
python train.py --conf recipes/settings.yaml 
```

学習条件は、yamlで書けるようにしていました。しばらく待つと、デフォルトの設定では `gmm_clb_to_slt.pkl`というファイルにGMMのパラメータが保存されます。

### パラメータ変換

学習したGMMを元に、メルケプストラムを変換します。

```
python vc.py --gmm gmm_clb_to_slt.pkl ~/data/vc/clb/arctic_a0028.json converted.json   
```

convered.json に変換後のパラメータが出力されます。

### 音声波形の再合成

```
python diff_synthesis.py --input ~/data/cmu_arctic/cmu_us_clb_arctic/wav/arctic_a0028.wav --mcep converted.json
```

converted.wav ができるので、聴いてみる。

以上、適当に覚えてることを書いてみました。
