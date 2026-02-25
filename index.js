const limit = 1000;
const token = "ff3862f3dfd3ce723b5515ee625821a136605ddb";

const queries = {
  MBG: [
    // "MBG since:2025-01-01 until:2025-01-07 lang:id", 169
    // "MBG since:2025-01-08 until:2025-01-14 lang:id", 169
    // "MBG since:2025-01-15 until:2025-01-21 lang:id", 159
    // "MBG since:2025-01-22 until:2025-01-28 lang:id", 129
    // "MBG since:2025-01-29 until:2025-02-04 lang:id", 172
    // "MBG since:2025-02-05 until:2025-02-11 lang:id", 126
    // "MBG since:2025-02-12 until:2025-02-18 lang:id", 126
    // "MBG since:2025-02-19 until:2025-03-04 lang:id", 147
    // "MBG since:2025-03-05 until:2025-03-11 lang:id", 176
    // "MBG since:2025-03-12 until:2025-03-18 lang:id", 152
    // "MBG since:2025-03-19 until:2025-04-04 lang:id", 126
    // "MBG since:2025-04-05 until:2025-04-11 lang:id", 114
    // "MBG since:2025-04-12 until:2025-04-18 lang:id", 150
    // "MBG since:2025-04-19 until:2025-05-04 lang:id", 232
    // "MBG since:2025-05-05 until:2025-05-11 lang:id", 195
    // "MBG since:2025-05-12 until:2025-05-18 lang:id", 200
    // "MBG since:2025-05-19 until:2025-06-04 lang:id", 160
    // "MBG since:2025-06-05 until:2025-06-11 lang:id", 162
    // "MBG since:2025-06-12 until:2025-06-18 lang:id", 166
    // "MBG since:2025-06-19 until:2025-07-04 lang:id", 208
    // "MBG since:2025-07-05 until:2025-07-11 lang:id", 145
    // "MBG since:2025-07-12 until:2025-07-18 lang:id", 140
    // "MBG since:2025-07-19 until:2025-08-04 lang:id", 210
    // "MBG since:2025-08-05 until:2025-08-11 lang:id", 187
    // "MBG since:2025-08-12 until:2025-08-18 lang:id", 158
    // "MBG since:2025-08-19 until:2025-09-04 lang:id", 214
    // "MBG since:2025-09-05 until:2025-09-11 lang:id", 168
    // "MBG since:2025-09-12 until:2025-09-18 lang:id", 195
    // "MBG since:2025-09-19 until:2025-10-04 lang:id", 252
    // "MBG since:2025-10-05 until:2025-10-11 lang:id", 213
    // "MBG since:2025-10-12 until:2025-10-18 lang:id", 208
    // "MBG since:2025-10-19 until:2025-11-04 lang:id", 255
    // "MBG since:2025-11-05 until:2025-11-11 lang:id", 199
    // "MBG since:2025-11-12 until:2025-11-18 lang:id", 219
    // "MBG since:2025-11-19 until:2025-12-04 lang:id", 223
    // "MBG since:2025-12-05 until:2025-12-11 lang:id", 184
    // "MBG since:2025-12-12 until:2025-12-18 lang:id", 223
    // "MBG since:2025-12-19 until:2025-12-26 lang:id", 174
    // "MBG since:2025-12-27 until:2025-12-31 lang:id", 181
  ],
  "RUU TNI": [
    // "RUU TNI OR #TolakRUUTNI OR #TolakDwifungsiABRI OR #TolakRevisiUUTNI since:2025-03-01 until:2025-03-03 lang:id",14
    // "RUU TNI OR #TolakRUUTNI OR #TolakDwifungsiABRI OR #TolakRevisiUUTNI since:2025-03-04 until:2025-03-06 lang:id",47
    // "RUU TNI OR #TolakRUUTNI OR #TolakDwifungsiABRI OR #TolakRevisiUUTNI since:2025-03-07 until:2025-03-09 lang:id", 21
    // "RUU TNI OR #TolakRUUTNI OR #TolakDwifungsiABRI OR #TolakRevisiUUTNI since:2025-03-10 until:2025-03-12 lang:id",57
    // "RUU TNI OR #TolakRUUTNI OR #TolakDwifungsiABRI OR #TolakRevisiUUTNI since:2025-03-13 until:2025-03-15 lang:id",64
    // "RUU TNI OR #TolakRUUTNI OR #TolakDwifungsiABRI OR #TolakRevisiUUTNI since:2025-03-16 until:2025-03-18 lang:id", 219
    // "RUU TNI OR #TolakRUUTNI OR #TolakDwifungsiABRI OR #TolakRevisiUUTNI since:2025-03-19 until:2025-03-21 lang:id", 235
    // "RUU TNI OR #TolakRUUTNI OR #TolakDwifungsiABRI OR #TolakRevisiUUTNI since:2025-03-22 until:2025-03-24 lang:id", 115
    // "RUU TNI OR #TolakRUUTNI OR #TolakDwifungsiABRI OR #TolakRevisiUUTNI since:2025-03-25 until:2025-03-27 lang:id", 192
    // "RUU TNI OR #TolakRUUTNI OR #TolakDwifungsiABRI OR #TolakRevisiUUTNI since:2025-03-28 until:2025-04-01 lang:id", 151
    // "RUU TNI OR #TolakRUUTNI OR #TolakDwifungsiABRI OR #TolakRevisiUUTNI since:2025-04-02 until:2025-04-04 lang:id", 121
    // "RUU TNI OR #TolakRUUTNI OR #TolakDwifungsiABRI OR #TolakRevisiUUTNI since:2025-04-05 until:2025-04-07 lang:id", 140
    // "RUU TNI OR #TolakRUUTNI OR #TolakDwifungsiABRI OR #TolakRevisiUUTNI since:2025-04-08 until:2025-04-10 lang:id", 140
    // "RUU TNI OR #TolakRUUTNI OR #TolakDwifungsiABRI OR #TolakRevisiUUTNI since:2025-04-11 until:2025-04-13 lang:id", 99
    // "RUU TNI OR #TolakRUUTNI OR #TolakDwifungsiABRI OR #TolakRevisiUUTNI since:2025-04-14 until:2025-04-16 lang:id", 143
    // "RUU TNI OR #TolakRUUTNI OR #TolakDwifungsiABRI OR #TolakRevisiUUTNI since:2025-04-17 until:2025-04-19 lang:id", 155
    // "RUU TNI OR #TolakRUUTNI OR #TolakDwifungsiABRI OR #TolakRevisiUUTNI since:2025-04-20 until:2025-04-22 lang:id", 59
    // "RUU TNI OR #TolakRUUTNI OR #TolakDwifungsiABRI OR #TolakRevisiUUTNI since:2025-04-23 until:2025-04-25 lang:id", 79
    "RUU TNI OR #TolakRUUTNI OR #TolakDwifungsiABRI OR #TolakRevisiUUTNI since:2025-04-26 until:2025-04-28 lang:id",
    "RUU TNI OR #TolakRUUTNI OR #TolakDwifungsiABRI OR #TolakRevisiUUTNI since:2025-04-29 until:2025-05-01 lang:id",
  ],
};
