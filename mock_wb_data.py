MOCK_ORDER =   {
  "next": 13833711,
  "orders": [
    {
      "address": {
        "fullAddress": "Челябинская область, г. Челябинск, 51-я улица Арабкира, д. 10А, кв. 42",
        "longitude": 44.519068,
        "latitude": 40.20192
      },
      "scanPrice": 1500,
      "deliveryType": "dbs",
      "supplyId": "WB-GI-92937123",
      "orderUid": "165918930_629fbc924b984618a44354475ca58675",
      "article": "one-ring-7548",
      "colorCode": "RAL 3017",
      "rid": "f884001e44e511edb8780242ac120002",
      "createdAt": "2022-05-04T07:56:29Z",
      "offices": [
        "Калуга"
      ],
      "skus": [
        "12345678998"
      ],
      "id": 13833711,
      "warehouseId": 658434,
      "nmId": 98765432,
      "chrtId": 987654321,
      "price": 1014,
      "convertedPrice": 28322,
      "currencyCode": 933,
      "convertedCurrencyCode": 643,
      "cargoType": 1,
      "comment": "Упакуйте в плёнку, пожалуйста",
      "isZeroOrder": "false"
    }
  ]
}

MOCK_STATUS = {
    "id": 13833711,
    "supplierStatus": "complete",
    "wbStatus": "sold"   # Важно для кэшбэка
}

MOCK_FEEDBACKS = {
  "data": {
    "countUnanswered": 52,
    "countArchive": 1000,
    "feedbacks": [
      {
        "id": "YX52RZEBhH9mrcYdEJuD",
        "text": "Спасибо, всё подошло",
        "pros": "Удобный",
        "cons": "Нет",
        "productValuation": 5,
        "createdDate": "2024-09-26T10:20:48+03:00",
        "state": "wbRu",
        "productDetails": {
          "imtId": 123456789,
          "nmId": 98765432,
          "productName": "ВАЗ",
          "supplierArticle": "DP02/черный",
          "supplierName": "ГП Реклама и услуги",
          "brandName": "Бест Трикотаж",
          "size": "0"
        },
        "video": {
          "previewImage": "https://videofeedback01.wbbasket.ru/8defc853-7f62-4d6d-b236-8a16cfb63128/preview.webp",
          "link": "https://videofeedback01.wbbasket.ru/8defc853-7f62-4d6d-b236-8a16cfb63128/index.m3u8",
          "durationSec": 10
        },
        "wasViewed": "true",
        "photoLinks": [
          {
            "fullSize": "https://feedback04.wbbasket.ru/vol1333/part133337/123456789/photos/fs.jpg",
            "miniSize": "https://feedback04.wbbasket.ru/vol1333/part133337/123456789/photos/ms.jpg"
          },
          {
            "fullSize": "https://feedback04.wbbasket.ru/vol1508/part150887/123456789/photos/fs.jpg",
            "miniSize": "https://feedback04.wbbasket.ru/vol1508/part150887/123456789/photos/ms.jpg"
          },
          {
            "fullSize": "https://feedback04.wbbasket.ru/vol1486/part148682/123456789/photos/fs.jpg",
            "miniSize": "https://feedback04.wbbasket.ru/vol1486/part148682/123456789/photos/ms.jpg"
          }
        ],
        "userName": "Николай",
        "matchingSize": "ok",
        "isAbleSupplierFeedbackValuation": "false",
        "supplierFeedbackValuation": 1,
        "isAbleSupplierProductValuation": "false",
        "supplierProductValuation": 2,
        "isAbleReturnProductOrders": "false",
        "returnProductOrdersDate": "2024-08-20T16:39:49Z",
        "bables": [
          "цена"
        ],
        "lastOrderShkId": 12345678998,
        "lastOrderCreatedAt": "2024-08-12T10:20:48+03:00",
        "color": "colorless",
        "subjectId": 219,
        "subjectName": "Футболки-поло",
        "parentFeedbackId": "null",
        "childFeedbackId": "bIjTCZDvJni7NGnLbUlf"
      }
    ]
  },
  "error": "false",
  "errorText": "",
  "additionalErrors": "null"
}


MOCK_PRODUCT_INFO = {
        "data": {
            "listGoods": [
                {
                    "nmID": 98765432,
                    "vendorCode": "07326060",
                    "sizes": [
                        {
                            "sizeID": 3123515574,
                            "price": 500,
                            "discountedPrice": 350,
                            "clubDiscountedPrice": 332.5,
                            "techSizeName": "42"
                        }
                    ],
                    "currencyIsoCode4217": "RUB",
                    "discount": 30,
                    "clubDiscount": 5,
                    "editableSizePrice": "true"
                }
            ]
        }
}


MOCK_CARD_INFO = {
  "cards": [
    {
      "nmID": 98765432,
      "imtID": 123654789,
      "nmUUID": "01bda0b1-5c0b-736c-b2be-d0a6543e9be",
      "subjectID": 2560,
      "subjectName": "AKF системы",
      "vendorCode": "wb7f6mumjr1",
      "brand": "Zaebrend",
      "title": "Vasdas",
      "photos": [
        {
          "big": "https://basket-10.wbbasket.ru/vol1592/part159206/159206280/images/big/1.webp",
          "c246x328": "https://basket-10.wbbasket.ru/vol1592/part159206/159206280/images/c246x328/1.webp",
          "c516x688": "https://basket-10.wbbasket.ru/vol1592/part159206/159206280/images/c516x688/1.webp",
          "square": "https://basket-10.wbbasket.ru/vol1592/part159206/159206280/images/square/1.webp",
          "tm": "https://basket-10.wbbasket.ru/vol1592/part159206/159206280/images/tm/1.webp"
        }
      ],
      "video": "https://videonme-basket-12.wbbasket.ru/vol137/part22557/225577433/hls/1440p/index.m3u8",
      "dimensions": {
        "length": 0,
        "width": 0,
        "height": 0,
        "isValid": "false"
      },
      "characteristics": [
        {
          "id": 14177449,
          "name": "Цвет",
          "value": [
            "красно-сиреневый"
          ]
        }
      ],
      "sizes": [
        {
          "chrtID": 316399238,
          "techSize": "0",
          "skus": [
            "987456321654"
          ]
        }
      ],
      "tags": [
        {
          "id": 592569,
          "name": "Популярный",
          "color": "D1CFD7"
        }
      ],
      "createdAt": "2023-12-06T11:17:00.96577Z",
      "updatedAt": "2023-12-06T11:17:00.96577Z"
    }
  ],
  "cursor": {
    "updatedAt": "2023-12-06T11:17:00.96577Z",
    "nmID": 123654123,
    "total": 1
  }
}

MOCK_CATEGORY = {
  "data": [
    {
      "subjectID": 2560,
      "parentID": 479,
      "subjectName": "3D очки",
      "parentName": "Электроника"
    },
    {
      "subjectID": 1152,
      "parentID": 858,
      "subjectName": "3D-принтеры",
      "parentName": "Оргтехника"
    }
  ],
  "error": "false",
  "errorText": "",
  "additionalErrors": "null"
}

