# U-Meking Sales Engine

一个本地Web应用程序，用于生成专业的产品目录和报价单。

## 功能特点

- **产品库存管理**: 添加、编辑、删除产品信息
- **产品目录生成器**: 生成专业的PDF目录（网格布局）
- **报价单生成器**: 为客户生成正式的PDF报价单
- **设置管理**: 配置公司信息、Logo、品牌颜色等

## 技术栈

- **前端/UI**: Streamlit
- **数据处理**: Pandas (CSV存储)
- **PDF生成**: ReportLab
- **图片处理**: Pillow (PIL)

## 安装步骤

1. 确保已安装 Python 3.8+

2. 安装依赖包：
```bash
pip install -r requirements.txt
```

3. 运行应用程序：
```bash
streamlit run app.py
```

4. 在浏览器中打开 http://localhost:8501

## 目录结构

```
├── app.py              # 主应用程序（Streamlit界面）
├── data_manager.py     # 数据管理模块（CSV读写、图片保存）
├── pdf_generator.py    # PDF生成模块（目录和报价单）
├── requirements.txt    # 依赖包列表
├── data/               # 数据存储目录
│   ├── products.csv    # 产品数据
│   └── settings.json   # 应用设置
└── assets/             # 资源文件目录
    ├── images/         # 产品图片
    └── company_logo.*  # 公司Logo
```

## 使用说明

### 1. 初始设置

首次使用时，建议先在"⚙️ Settings"页面配置：
- 公司名称、地址、联系方式
- 上传公司Logo
- 设置品牌颜色
- 配置默认条款

### 2. 添加产品

在"📦 Product Inventory"页面：
- 填写产品SKU、名称、分类
- 输入产品描述（每行一个规格）
- 设置单价和最小订购量
- 上传产品图片
- 设置包装信息（装箱率、纸箱尺寸、毛重）

### 3. 生成产品目录

在"📚 Catalog Creator"页面：
- 选择要包含的产品
- 设置目录编号和日期
- 点击"Generate Catalog PDF"
- 下载生成的PDF文件

### 4. 生成报价单

在"💰 Quotation Builder"页面：
- 填写客户信息
- 添加产品并设置数量
- 设置运费和运输条款
- 点击"Generate Quote PDF"
- 下载生成的PDF文件

## 注意事项

- 产品数据存储在本地CSV文件中，请定期备份
- 图片会被自动压缩以优化存储和PDF大小
- PDF使用A4纸张尺寸
- 建议产品图片尺寸为正方形（如800x800像素）

## 许可证

© 2026 Guangzhou U-meking Co., Ltd. All rights reserved.
