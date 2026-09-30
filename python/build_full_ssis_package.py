"""
build_full_ssis_package.py
Generates the complete Visual Studio SSIS package Package.dtsx with full
Data Flow internal components (OLE DB Sources, Flat File Source, Derived Column,
3 sequential Lookups, and OLE DB Destinations) with exact graphical layout.
"""
import os

out_path = r"ssis\Olist_ETL\Package.dtsx"

package_xml = '''<?xml version="1.0"?>
<DTS:Executable xmlns:DTS="www.microsoft.com/SqlServer/Dts"
  DTS:refId="Package"
  DTS:CreationDate="9/30/2026 8:52:16 AM"
  DTS:CreationName="Microsoft.Package"
  DTS:CreatorComputerName="ACER"
  DTS:CreatorName="ACER\\thuva"
  DTS:DTSID="{7DBD5534-B5B6-4FB3-97DC-E3AFFA12EBB3}"
  DTS:ExecutableType="Microsoft.Package"
  DTS:LastModifiedProductVersion="17.0.1016.0"
  DTS:LocaleID="1033"
  DTS:ObjectName="Package"
  DTS:PackageType="5"
  DTS:VersionGUID="{A9939191-603C-43A1-A037-5D8A7A35B798}">
  <DTS:Property DTS:Name="PackageFormatVersion">8</DTS:Property>
  <DTS:ConnectionManagers>
    <DTS:ConnectionManager
      DTS:refId="Package.ConnectionManagers[Olist_OLTP]"
      DTS:CreationName="OLEDB"
      DTS:DTSID="{7E9D9346-6D3E-4B07-B45A-8EF1E2C04D81}"
      DTS:ObjectName="Olist_OLTP">
      <DTS:ObjectData>
        <DTS:ConnectionManager
          DTS:ConnectionString="Data Source=localhost;Initial Catalog=Olist_OLTP;Provider=SQLNCLI11.1;Integrated Security=SSPI;Auto Translate=False;" />
      </DTS:ObjectData>
    </DTS:ConnectionManager>
    <DTS:ConnectionManager
      DTS:refId="Package.ConnectionManagers[Olist_DW]"
      DTS:CreationName="OLEDB"
      DTS:DTSID="{9C623C6D-5509-4C51-B9D7-BE480D9F0A3E}"
      DTS:ObjectName="Olist_DW">
      <DTS:ObjectData>
        <DTS:ConnectionManager
          DTS:ConnectionString="Data Source=localhost;Initial Catalog=Olist_DW;Provider=SQLNCLI11.1;Integrated Security=SSPI;Auto Translate=False;" />
      </DTS:ObjectData>
    </DTS:ConnectionManager>
    <DTS:ConnectionManager
      DTS:refId="Package.ConnectionManagers[Products_CSV]"
      DTS:CreationName="FLATFILE"
      DTS:DTSID="{47A46B55-5B26-444F-A299-8260D0CD47F5}"
      DTS:ObjectName="Products_CSV">
      <DTS:ObjectData>
        <DTS:ConnectionManager
          DTS:Format="Delimited"
          DTS:LocaleID="1033"
          DTS:HeaderRowDelimiter="_x000D__x000A_"
          DTS:ColumnNamesInFirstDataRow="True"
          DTS:RowDelimiter=""
          DTS:ConnectionString="c:\\Users\\thuva\\OneDrive\\Desktop\\DWBI Project\\Dataset\\olist_products_dataset.csv">
        </DTS:ConnectionManager>
      </DTS:ObjectData>
    </DTS:ConnectionManager>
  </DTS:ConnectionManagers>
  <DTS:Variables />
  <DTS:Executables>
    <!-- ====================================================================== -->
    <!-- 1. DATA FLOW TASK: Load_Dim_Customer                                    -->
    <!-- ====================================================================== -->
    <DTS:Executable
      DTS:refId="Package\\Load_Dim_Customer"
      DTS:CreationName="Microsoft.Pipeline"
      DTS:Description="Data Flow Task - Extracts Customers from Source and fast-loads Dim_Customer"
      DTS:DTSID="{A24B91E3-8821-4E8F-A332-6A15E8D291F0}"
      DTS:ExecutableType="Microsoft.Pipeline"
      DTS:LocaleID="-1"
      DTS:ObjectName="Load_Dim_Customer"
      DTS:TaskContact="Performs high-performance data extraction, transformation and loading;Microsoft Corporation; Microsoft SQL Server; (C) Microsoft Corporation; All Rights Reserved;">
      <DTS:Variables />
      <DTS:ObjectData>
        <pipeline version="1">
          <components>
            <component
              refId="Package\\Load_Dim_Customer\\OLE DB Source"
              componentClassID="Microsoft.OLEDBSource"
              contactInfo="OLE DB Source;Microsoft Corporation; Microsoft SQL Server; (C) Microsoft Corporation; All Rights Reserved;"
              description="OLE DB Source - olist_customers_dataset"
              name="OLE DB Source"
              usesDispositions="true"
              version="7">
              <properties>
                <property dataType="System.Int32" description="Command timeout" name="CommandTimeout">0</property>
                <property dataType="System.String" description="OpenRowset" name="OpenRowset">[dbo].[olist_customers_dataset]</property>
                <property dataType="System.Int32" description="AccessMode" name="AccessMode" typeConverter="AccessMode">0</property>
              </properties>
              <connections>
                <connection
                  refId="Package\\Load_Dim_Customer\\OLE DB Source.Connections[OleDbConnection]"
                  connectionManagerID="Package.ConnectionManagers[Olist_OLTP]"
                  connectionManagerRefId="Package.ConnectionManagers[Olist_OLTP]"
                  description="Source database connection"
                  name="OleDbConnection" />
              </connections>
              <outputs>
                <output
                  refId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Output]"
                  name="OLE DB Source Output">
                  <externalMetadataColumns isUsed="False" />
                </output>
              </outputs>
            </component>
            <component
              refId="Package\\Load_Dim_Customer\\OLE DB Destination"
              componentClassID="Microsoft.OLEDBDestination"
              contactInfo="OLE DB Destination;Microsoft Corporation; Microsoft SQL Server; (C) Microsoft Corporation; All Rights Reserved;"
              description="OLE DB Destination - Dim_Customer"
              name="OLE DB Destination"
              usesDispositions="true"
              version="4">
              <properties>
                <property dataType="System.Int32" description="Command timeout" name="CommandTimeout">0</property>
                <property dataType="System.String" description="OpenRowset" name="OpenRowset">[dbo].[Dim_Customer]</property>
                <property dataType="System.Int32" description="AccessMode" name="AccessMode" typeConverter="AccessMode">3</property>
                <property dataType="System.Boolean" description="FastLoadKeepIdentity" name="FastLoadKeepIdentity">false</property>
                <property dataType="System.Boolean" description="FastLoadKeepNulls" name="FastLoadKeepNulls">true</property>
                <property dataType="System.String" description="FastLoadOptions" name="FastLoadOptions">TABLOCK,CHECK_CONSTRAINTS</property>
              </properties>
              <connections>
                <connection
                  refId="Package\\Load_Dim_Customer\\OLE DB Destination.Connections[OleDbConnection]"
                  connectionManagerID="Package.ConnectionManagers[Olist_DW]"
                  connectionManagerRefId="Package.ConnectionManagers[Olist_DW]"
                  description="Destination Data Warehouse connection"
                  name="OleDbConnection" />
              </connections>
              <inputs>
                <input
                  refId="Package\\Load_Dim_Customer\\OLE DB Destination.Inputs[OLE DB Destination Input]"
                  errorOrTruncationOperation="Insert"
                  errorRowDisposition="FailComponent"
                  hasSideEffects="true"
                  name="OLE DB Destination Input">
                  <externalMetadataColumns isUsed="False" />
                </input>
              </inputs>
            </component>
          </components>
          <paths>
            <path
              refId="Package\\Load_Dim_Customer.Paths[OLE DB Source Output]"
              endId="Package\\Load_Dim_Customer\\OLE DB Destination.Inputs[OLE DB Destination Input]"
              name="OLE DB Source Output"
              startId="Package\\Load_Dim_Customer\\OLE DB Source.Outputs[OLE DB Source Output]" />
          </paths>
        </pipeline>
      </DTS:ObjectData>
    </DTS:Executable>

    <!-- ====================================================================== -->
    <!-- 2. DATA FLOW TASK: Load_Dim_Product                                     -->
    <!-- ====================================================================== -->
    <DTS:Executable
      DTS:refId="Package\\Load_Dim_Product"
      DTS:CreationName="Microsoft.Pipeline"
      DTS:Description="Data Flow Task - Products CSV with Derived Column REPLACENULL"
      DTS:DTSID="{B35C82F4-9932-5F9A-B443-7B26F9E3A201}"
      DTS:ExecutableType="Microsoft.Pipeline"
      DTS:LocaleID="-1"
      DTS:ObjectName="Load_Dim_Product"
      DTS:TaskContact="Performs high-performance data extraction, transformation and loading;Microsoft Corporation; Microsoft SQL Server; (C) Microsoft Corporation; All Rights Reserved;">
      <DTS:Variables />
      <DTS:ObjectData>
        <pipeline version="1">
          <components>
            <component
              refId="Package\\Load_Dim_Product\\Flat File Source"
              componentClassID="Microsoft.FlatFileSource"
              contactInfo="Flat File Source;Microsoft Corporation; Microsoft SQL Server; (C) Microsoft Corporation; All Rights Reserved;"
              description="Flat File Source - Products CSV"
              name="Flat File Source">
              <properties>
                <property dataType="System.Boolean" description="RetainNulls" name="RetainNulls">false</property>
                <property dataType="System.String" description="FileNameColumnName" name="FileNameColumnName"></property>
              </properties>
              <connections>
                <connection
                  refId="Package\\Load_Dim_Product\\Flat File Source.Connections[FlatFileConnection]"
                  connectionManagerID="Package.ConnectionManagers[Products_CSV]"
                  connectionManagerRefId="Package.ConnectionManagers[Products_CSV]"
                  name="FlatFileConnection" />
              </connections>
              <outputs>
                <output
                  refId="Package\\Load_Dim_Product\\Flat File Source.Outputs[Flat File Source Output]"
                  name="Flat File Source Output">
                  <externalMetadataColumns isUsed="False" />
                </output>
              </outputs>
            </component>
            <component
              refId="Package\\Load_Dim_Product\\Derived Column"
              componentClassID="Microsoft.DerivedColumn"
              contactInfo="Derived Column;Microsoft Corporation; Microsoft SQL Server; (C) Microsoft Corporation; All Rights Reserved;"
              description="Updates column values using expressions (REPLACENULL)"
              name="Derived Column"
              usesDispositions="true">
              <inputs>
                <input
                  refId="Package\\Load_Dim_Product\\Derived Column.Inputs[Derived Column Input]"
                  description="Input to the Derived Column Transformation"
                  name="Derived Column Input">
                  <externalMetadataColumns isUsed="False" />
                </input>
              </inputs>
              <outputs>
                <output
                  refId="Package\\Load_Dim_Product\\Derived Column.Outputs[Derived Column Output]"
                  description="Default Output of the Derived Column Transformation"
                  exclusionGroup="1"
                  name="Derived Column Output"
                  synchronousInputId="Package\\Load_Dim_Product\\Derived Column.Inputs[Derived Column Input]">
                  <externalMetadataColumns isUsed="False" />
                </output>
              </outputs>
            </component>
            <component
              refId="Package\\Load_Dim_Product\\OLE DB Destination"
              componentClassID="Microsoft.OLEDBDestination"
              contactInfo="OLE DB Destination;Microsoft Corporation; Microsoft SQL Server; (C) Microsoft Corporation; All Rights Reserved;"
              description="OLE DB Destination - Dim_Product"
              name="OLE DB Destination"
              usesDispositions="true"
              version="4">
              <properties>
                <property dataType="System.Int32" description="Command timeout" name="CommandTimeout">0</property>
                <property dataType="System.String" description="OpenRowset" name="OpenRowset">[dbo].[Dim_Product]</property>
                <property dataType="System.Int32" description="AccessMode" name="AccessMode" typeConverter="AccessMode">3</property>
                <property dataType="System.Boolean" description="FastLoadKeepIdentity" name="FastLoadKeepIdentity">false</property>
                <property dataType="System.Boolean" description="FastLoadKeepNulls" name="FastLoadKeepNulls">true</property>
                <property dataType="System.String" description="FastLoadOptions" name="FastLoadOptions">TABLOCK,CHECK_CONSTRAINTS</property>
              </properties>
              <connections>
                <connection
                  refId="Package\\Load_Dim_Product\\OLE DB Destination.Connections[OleDbConnection]"
                  connectionManagerID="Package.ConnectionManagers[Olist_DW]"
                  connectionManagerRefId="Package.ConnectionManagers[Olist_DW]"
                  description="Destination connection"
                  name="OleDbConnection" />
              </connections>
              <inputs>
                <input
                  refId="Package\\Load_Dim_Product\\OLE DB Destination.Inputs[OLE DB Destination Input]"
                  errorOrTruncationOperation="Insert"
                  errorRowDisposition="FailComponent"
                  hasSideEffects="true"
                  name="OLE DB Destination Input">
                  <externalMetadataColumns isUsed="False" />
                </input>
              </inputs>
            </component>
          </components>
          <paths>
            <path
              refId="Package\\Load_Dim_Product.Paths[Flat File Source Output]"
              endId="Package\\Load_Dim_Product\\Derived Column.Inputs[Derived Column Input]"
              name="Flat File Source Output"
              startId="Package\\Load_Dim_Product\\Flat File Source.Outputs[Flat File Source Output]" />
            <path
              refId="Package\\Load_Dim_Product.Paths[Derived Column Output]"
              endId="Package\\Load_Dim_Product\\OLE DB Destination.Inputs[OLE DB Destination Input]"
              name="Derived Column Output"
              startId="Package\\Load_Dim_Product\\Derived Column.Outputs[Derived Column Output]" />
          </paths>
        </pipeline>
      </DTS:ObjectData>
    </DTS:Executable>

    <!-- ====================================================================== -->
    <!-- 3. DATA FLOW TASK: Load_Fact_Orders                                     -->
    <!-- ====================================================================== -->
    <DTS:Executable
      DTS:refId="Package\\Load_Fact_Orders"
      DTS:CreationName="Microsoft.Pipeline"
      DTS:Description="Data Flow Task - Extracts Delivered Orders with Lookups"
      DTS:DTSID="{C46D93A5-AA43-6AAB-C554-8C370AF4B312}"
      DTS:ExecutableType="Microsoft.Pipeline"
      DTS:LocaleID="-1"
      DTS:ObjectName="Load_Fact_Orders"
      DTS:TaskContact="Performs high-performance data extraction, transformation and loading;Microsoft Corporation; Microsoft SQL Server; (C) Microsoft Corporation; All Rights Reserved;">
      <DTS:Variables />
      <DTS:ObjectData>
        <pipeline version="1">
          <components>
            <component
              refId="Package\\Load_Fact_Orders\\OLE DB Source"
              componentClassID="Microsoft.OLEDBSource"
              contactInfo="OLE DB Source;Microsoft Corporation; Microsoft SQL Server; (C) Microsoft Corporation; All Rights Reserved;"
              description="OLE DB Source - Delivered Orders Extraction"
              name="OLE DB Source"
              usesDispositions="true"
              version="7">
              <properties>
                <property dataType="System.Int32" description="Command timeout" name="CommandTimeout">0</property>
                <property dataType="System.String" description="SqlCommand" name="SqlCommand">SELECT o.order_id, oi.order_item_id, o.customer_id, oi.product_id, oi.seller_id, CONVERT(INT, CONVERT(VARCHAR(8), o.order_purchase_timestamp, 112)) AS DateKey, oi.price, oi.freight_value, (oi.price + oi.freight_value) AS TotalOrderValue, DATEDIFF(day, o.order_purchase_timestamp, o.order_delivered_customer_date) AS DeliveryTimeDays FROM olist_orders_dataset o JOIN olist_order_items_dataset oi ON o.order_id = oi.order_id WHERE o.order_status = 'delivered';</property>
                <property dataType="System.Int32" description="AccessMode" name="AccessMode" typeConverter="AccessMode">2</property>
              </properties>
              <connections>
                <connection
                  refId="Package\\Load_Fact_Orders\\OLE DB Source.Connections[OleDbConnection]"
                  connectionManagerID="Package.ConnectionManagers[Olist_OLTP]"
                  connectionManagerRefId="Package.ConnectionManagers[Olist_OLTP]"
                  name="OleDbConnection" />
              </connections>
              <outputs>
                <output
                  refId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output]"
                  name="OLE DB Source Output">
                  <externalMetadataColumns isUsed="False" />
                </output>
              </outputs>
            </component>
            <component
              refId="Package\\Load_Fact_Orders\\Customer Lookup"
              componentClassID="Microsoft.Lookup"
              contactInfo="Lookup;Microsoft Corporation; Microsoft SQL Server; (C) Microsoft Corporation; All Rights Reserved;"
              description="Lookup CustomerSK from Dim_Customer"
              name="Customer Lookup"
              usesDispositions="true"
              version="6">
              <properties>
                <property dataType="System.String" description="SqlCommand" name="SqlCommand">SELECT CustomerSK, CustomerBK FROM [dbo].[Dim_Customer]</property>
                <property dataType="System.Int32" description="NoMatchBehavior" name="NoMatchBehavior" typeConverter="NoMatchBehavior">0</property>
              </properties>
              <connections>
                <connection
                  refId="Package\\Load_Fact_Orders\\Customer Lookup.Connections[OleDbConnection]"
                  connectionManagerID="Package.ConnectionManagers[Olist_DW]"
                  connectionManagerRefId="Package.ConnectionManagers[Olist_DW]"
                  name="OleDbConnection" />
              </connections>
              <inputs>
                <input
                  refId="Package\\Load_Fact_Orders\\Customer Lookup.Inputs[Lookup Input]"
                  name="Lookup Input">
                  <externalMetadataColumns isUsed="False" />
                </input>
              </inputs>
              <outputs>
                <output
                  refId="Package\\Load_Fact_Orders\\Customer Lookup.Outputs[Lookup Match Output]"
                  errorOrTruncationOperation="Lookup"
                  errorRowDisposition="IgnoreFailure"
                  exclusionGroup="1"
                  name="Lookup Match Output"
                  synchronousInputId="Package\\Load_Fact_Orders\\Customer Lookup.Inputs[Lookup Input]">
                  <externalMetadataColumns isUsed="False" />
                </output>
                <output
                  refId="Package\\Load_Fact_Orders\\Customer Lookup.Outputs[Lookup No Match Output]"
                  description="The Lookup output that handles rows with no matching entries in the reference dataset."
                  exclusionGroup="1"
                  name="Lookup No Match Output"
                  synchronousInputId="Package\\Load_Fact_Orders\\Customer Lookup.Inputs[Lookup Input]">
                  <externalMetadataColumns isUsed="False" />
                </output>
              </outputs>
            </component>
            <component
              refId="Package\\Load_Fact_Orders\\Product Lookup"
              componentClassID="Microsoft.Lookup"
              contactInfo="Lookup;Microsoft Corporation; Microsoft SQL Server; (C) Microsoft Corporation; All Rights Reserved;"
              description="Lookup ProductSK from Dim_Product"
              name="Product Lookup"
              usesDispositions="true"
              version="6">
              <properties>
                <property dataType="System.String" description="SqlCommand" name="SqlCommand">SELECT ProductSK, ProductBK FROM [dbo].[Dim_Product]</property>
                <property dataType="System.Int32" description="NoMatchBehavior" name="NoMatchBehavior" typeConverter="NoMatchBehavior">0</property>
              </properties>
              <connections>
                <connection
                  refId="Package\\Load_Fact_Orders\\Product Lookup.Connections[OleDbConnection]"
                  connectionManagerID="Package.ConnectionManagers[Olist_DW]"
                  connectionManagerRefId="Package.ConnectionManagers[Olist_DW]"
                  name="OleDbConnection" />
              </connections>
              <inputs>
                <input
                  refId="Package\\Load_Fact_Orders\\Product Lookup.Inputs[Lookup Input]"
                  name="Lookup Input">
                  <externalMetadataColumns isUsed="False" />
                </input>
              </inputs>
              <outputs>
                <output
                  refId="Package\\Load_Fact_Orders\\Product Lookup.Outputs[Lookup Match Output]"
                  errorOrTruncationOperation="Lookup"
                  errorRowDisposition="IgnoreFailure"
                  exclusionGroup="1"
                  name="Lookup Match Output"
                  synchronousInputId="Package\\Load_Fact_Orders\\Product Lookup.Inputs[Lookup Input]">
                  <externalMetadataColumns isUsed="False" />
                </output>
                <output
                  refId="Package\\Load_Fact_Orders\\Product Lookup.Outputs[Lookup No Match Output]"
                  exclusionGroup="1"
                  name="Lookup No Match Output"
                  synchronousInputId="Package\\Load_Fact_Orders\\Product Lookup.Inputs[Lookup Input]">
                  <externalMetadataColumns isUsed="False" />
                </output>
              </outputs>
            </component>
            <component
              refId="Package\\Load_Fact_Orders\\Seller Lookup"
              componentClassID="Microsoft.Lookup"
              contactInfo="Lookup;Microsoft Corporation; Microsoft SQL Server; (C) Microsoft Corporation; All Rights Reserved;"
              description="Lookup SellerSK from Dim_Seller with Ignore Failure"
              name="Seller Lookup"
              usesDispositions="true"
              version="6">
              <properties>
                <property dataType="System.String" description="SqlCommand" name="SqlCommand">SELECT SellerSK, SellerBK FROM [dbo].[Dim_Seller]</property>
                <!-- NoMatchBehavior = 1: Ignore failure (assigns NULL for missing keys) -->
                <property dataType="System.Int32" description="NoMatchBehavior" name="NoMatchBehavior" typeConverter="NoMatchBehavior">1</property>
              </properties>
              <connections>
                <connection
                  refId="Package\\Load_Fact_Orders\\Seller Lookup.Connections[OleDbConnection]"
                  connectionManagerID="Package.ConnectionManagers[Olist_DW]"
                  connectionManagerRefId="Package.ConnectionManagers[Olist_DW]"
                  name="OleDbConnection" />
              </connections>
              <inputs>
                <input
                  refId="Package\\Load_Fact_Orders\\Seller Lookup.Inputs[Lookup Input]"
                  name="Lookup Input">
                  <externalMetadataColumns isUsed="False" />
                </input>
              </inputs>
              <outputs>
                <output
                  refId="Package\\Load_Fact_Orders\\Seller Lookup.Outputs[Lookup Match Output]"
                  errorOrTruncationOperation="Lookup"
                  errorRowDisposition="IgnoreFailure"
                  exclusionGroup="1"
                  name="Lookup Match Output"
                  synchronousInputId="Package\\Load_Fact_Orders\\Seller Lookup.Inputs[Lookup Input]">
                  <externalMetadataColumns isUsed="False" />
                </output>
                <output
                  refId="Package\\Load_Fact_Orders\\Seller Lookup.Outputs[Lookup No Match Output]"
                  exclusionGroup="1"
                  name="Lookup No Match Output"
                  synchronousInputId="Package\\Load_Fact_Orders\\Seller Lookup.Inputs[Lookup Input]">
                  <externalMetadataColumns isUsed="False" />
                </output>
              </outputs>
            </component>
            <component
              refId="Package\\Load_Fact_Orders\\OLE DB Destination"
              componentClassID="Microsoft.OLEDBDestination"
              contactInfo="OLE DB Destination;Microsoft Corporation; Microsoft SQL Server; (C) Microsoft Corporation; All Rights Reserved;"
              description="OLE DB Destination - Fact_Orders"
              name="OLE DB Destination"
              usesDispositions="true"
              version="4">
              <properties>
                <property dataType="System.Int32" description="Command timeout" name="CommandTimeout">0</property>
                <property dataType="System.String" description="OpenRowset" name="OpenRowset">[dbo].[Fact_Orders]</property>
                <property dataType="System.Int32" description="AccessMode" name="AccessMode" typeConverter="AccessMode">3</property>
                <property dataType="System.Boolean" description="FastLoadKeepIdentity" name="FastLoadKeepIdentity">false</property>
                <property dataType="System.Boolean" description="FastLoadKeepNulls" name="FastLoadKeepNulls">true</property>
                <property dataType="System.String" description="FastLoadOptions" name="FastLoadOptions">TABLOCK,CHECK_CONSTRAINTS</property>
              </properties>
              <connections>
                <connection
                  refId="Package\\Load_Fact_Orders\\OLE DB Destination.Connections[OleDbConnection]"
                  connectionManagerID="Package.ConnectionManagers[Olist_DW]"
                  connectionManagerRefId="Package.ConnectionManagers[Olist_DW]"
                  name="OleDbConnection" />
              </connections>
              <inputs>
                <input
                  refId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input]"
                  errorOrTruncationOperation="Insert"
                  errorRowDisposition="FailComponent"
                  hasSideEffects="true"
                  name="OLE DB Destination Input">
                  <externalMetadataColumns isUsed="False" />
                </input>
              </inputs>
            </component>
          </components>
          <paths>
            <path
              refId="Package\\Load_Fact_Orders.Paths[OLE DB Source Output]"
              endId="Package\\Load_Fact_Orders\\Customer Lookup.Inputs[Lookup Input]"
              name="OLE DB Source Output"
              startId="Package\\Load_Fact_Orders\\OLE DB Source.Outputs[OLE DB Source Output]" />
            <path
              refId="Package\\Load_Fact_Orders.Paths[Customer Match Output]"
              endId="Package\\Load_Fact_Orders\\Product Lookup.Inputs[Lookup Input]"
              name="Customer Match Output"
              startId="Package\\Load_Fact_Orders\\Customer Lookup.Outputs[Lookup Match Output]" />
            <path
              refId="Package\\Load_Fact_Orders.Paths[Product Match Output]"
              endId="Package\\Load_Fact_Orders\\Seller Lookup.Inputs[Lookup Input]"
              name="Product Match Output"
              startId="Package\\Load_Fact_Orders\\Product Lookup.Outputs[Lookup Match Output]" />
            <path
              refId="Package\\Load_Fact_Orders.Paths[Seller Match Output]"
              endId="Package\\Load_Fact_Orders\\OLE DB Destination.Inputs[OLE DB Destination Input]"
              name="Seller Match Output"
              startId="Package\\Load_Fact_Orders\\Seller Lookup.Outputs[Lookup Match Output]" />
          </paths>
        </pipeline>
      </DTS:ObjectData>
    </DTS:Executable>
  </DTS:Executables>

  <DTS:PrecedenceConstraints>
    <DTS:PrecedenceConstraint
      DTS:refId="Package.PrecedenceConstraints[Constraint_Customer_to_Product]"
      DTS:CreationName=""
      DTS:DTSID="{D57EA4B6-BB54-7BBC-D665-9D481BA5C423}"
      DTS:From="Package\\Load_Dim_Customer"
      DTS:LogicalAnd="True"
      DTS:ObjectName="Constraint_Customer_to_Product"
      DTS:To="Package\\Load_Dim_Product" />
    <DTS:PrecedenceConstraint
      DTS:refId="Package.PrecedenceConstraints[Constraint_Product_to_Fact]"
      DTS:CreationName=""
      DTS:DTSID="{E68FB5C7-CC65-8CCD-E776-AE592CB6D534}"
      DTS:From="Package\\Load_Dim_Product"
      DTS:LogicalAnd="True"
      DTS:ObjectName="Constraint_Product_to_Fact"
      DTS:To="Package\\Load_Fact_Orders" />
  </DTS:PrecedenceConstraints>

  <!-- ====================================================================== -->
  <!-- DESIGN TIME PROPERTIES: Graphical Canvas Layout                         -->
  <!-- ====================================================================== -->
  <DTS:DesignTimeProperties><![CDATA[<?xml version="1.0"?>
<GraphLayout xmlns="clr-namespace:Microsoft.SqlServer.IntegrationServices.Designer.Model.Serialization;assembly=Microsoft.SqlServer.IntegrationServices.Graph" xmlns:mssgle="clr-namespace:Microsoft.SqlServer.Graph.LayoutEngine;assembly=Microsoft.SqlServer.Graph" xmlns:assembly="http://schemas.microsoft.com/winfx/2006/xaml">
  <!-- Control Flow Canvas -->
  <NodeLayout
    Size="195,42"
    Id="Package\\Load_Dim_Customer"
    TopLeft="160,40" />
  <NodeLayout
    Size="185,42"
    Id="Package\\Load_Dim_Product"
    TopLeft="165,130" />
  <NodeLayout
    Size="180,42"
    Id="Package\\Load_Fact_Orders"
    TopLeft="168,220" />
  <EdgeLayout
    Id="Package.PrecedenceConstraints[Constraint_Customer_to_Product]"
    TopLeft="257.5,82">
    <EdgeLayout.Curve>
      <mssgle:Curve
        StartConnector="{assembly:Null}"
        EndConnector="0,48"
        Start="0,0"
        End="0,40.5">
        <mssgle:Curve.Segments>
          <mssgle:SegmentCollection
            Capacity="5">
            <mssgle:LineSegment
              End="0,40.5" />
          </mssgle:SegmentCollection>
        </mssgle:Curve.Segments>
      </mssgle:Curve>
    </EdgeLayout.Curve>
    <EdgeLayout.Labels>
      <EdgeLabelCollection />
    </EdgeLayout.Labels>
  </EdgeLayout>
  <EdgeLayout
    Id="Package.PrecedenceConstraints[Constraint_Product_to_Fact]"
    TopLeft="257.5,172">
    <EdgeLayout.Curve>
      <mssgle:Curve
        StartConnector="{assembly:Null}"
        EndConnector="0,48"
        Start="0,0"
        End="0,40.5">
        <mssgle:Curve.Segments>
          <mssgle:SegmentCollection
            Capacity="5">
            <mssgle:LineSegment
              End="0,40.5" />
          </mssgle:SegmentCollection>
        </mssgle:Curve.Segments>
      </mssgle:Curve>
    </EdgeLayout.Curve>
    <EdgeLayout.Labels>
      <EdgeLabelCollection />
    </EdgeLayout.Labels>
  </EdgeLayout>

  <!-- Data Flow Canvas 1: Load_Dim_Customer -->
  <NodeLayout
    Size="150,42"
    Id="Package\\Load_Dim_Customer\\OLE DB Source"
    TopLeft="230,50" />
  <NodeLayout
    Size="171,42"
    Id="Package\\Load_Dim_Customer\\OLE DB Destination"
    TopLeft="220,160" />
  <EdgeLayout
    Id="Package\\Load_Dim_Customer.Paths[OLE DB Source Output]"
    TopLeft="305,92">
    <EdgeLayout.Curve>
      <mssgle:Curve
        StartConnector="{assembly:Null}"
        EndConnector="0,68"
        Start="0,0"
        End="0,60.5">
        <mssgle:Curve.Segments>
          <mssgle:SegmentCollection
            Capacity="5">
            <mssgle:LineSegment
              End="0,60.5" />
          </mssgle:SegmentCollection>
        </mssgle:Curve.Segments>
      </mssgle:Curve>
    </EdgeLayout.Curve>
    <EdgeLayout.Labels>
      <EdgeLabelCollection />
    </EdgeLayout.Labels>
  </EdgeLayout>

  <!-- Data Flow Canvas 2: Load_Dim_Product -->
  <NodeLayout
    Size="151,42"
    Id="Package\\Load_Dim_Product\\Flat File Source"
    TopLeft="230,40" />
  <NodeLayout
    Size="154,42"
    Id="Package\\Load_Dim_Product\\Derived Column"
    TopLeft="228,130" />
  <NodeLayout
    Size="171,42"
    Id="Package\\Load_Dim_Product\\OLE DB Destination"
    TopLeft="220,220" />
  <EdgeLayout
    Id="Package\\Load_Dim_Product.Paths[Flat File Source Output]"
    TopLeft="305,82">
    <EdgeLayout.Curve>
      <mssgle:Curve
        StartConnector="{assembly:Null}"
        EndConnector="0,48"
        Start="0,0"
        End="0,40.5">
        <mssgle:Curve.Segments>
          <mssgle:SegmentCollection
            Capacity="5">
            <mssgle:LineSegment
              End="0,40.5" />
          </mssgle:SegmentCollection>
        </mssgle:Curve.Segments>
      </mssgle:Curve>
    </EdgeLayout.Curve>
    <EdgeLayout.Labels>
      <EdgeLabelCollection />
    </EdgeLayout.Labels>
  </EdgeLayout>
  <EdgeLayout
    Id="Package\\Load_Dim_Product.Paths[Derived Column Output]"
    TopLeft="305,172">
    <EdgeLayout.Curve>
      <mssgle:Curve
        StartConnector="{assembly:Null}"
        EndConnector="0,48"
        Start="0,0"
        End="0,40.5">
        <mssgle:Curve.Segments>
          <mssgle:SegmentCollection
            Capacity="5">
            <mssgle:LineSegment
              End="0,40.5" />
          </mssgle:SegmentCollection>
        </mssgle:Curve.Segments>
      </mssgle:Curve>
    </EdgeLayout.Curve>
    <EdgeLayout.Labels>
      <EdgeLabelCollection />
    </EdgeLayout.Labels>
  </EdgeLayout>

  <!-- Data Flow Canvas 3: Load_Fact_Orders -->
  <NodeLayout
    Size="150,42"
    Id="Package\\Load_Fact_Orders\\OLE DB Source"
    TopLeft="245,30" />
  <NodeLayout
    Size="163,42"
    Id="Package\\Load_Fact_Orders\\Customer Lookup"
    TopLeft="238,110" />
  <NodeLayout
    Size="154,42"
    Id="Package\\Load_Fact_Orders\\Product Lookup"
    TopLeft="243,190" />
  <NodeLayout
    Size="144,42"
    Id="Package\\Load_Fact_Orders\\Seller Lookup"
    TopLeft="248,270" />
  <NodeLayout
    Size="171,42"
    Id="Package\\Load_Fact_Orders\\OLE DB Destination"
    TopLeft="234,350" />
  <EdgeLayout
    Id="Package\\Load_Fact_Orders.Paths[OLE DB Source Output]"
    TopLeft="320,72">
    <EdgeLayout.Curve>
      <mssgle:Curve
        StartConnector="{assembly:Null}"
        EndConnector="0,38"
        Start="0,0"
        End="0,30.5">
        <mssgle:Curve.Segments>
          <mssgle:SegmentCollection
            Capacity="5">
            <mssgle:LineSegment
              End="0,30.5" />
          </mssgle:SegmentCollection>
        </mssgle:Curve.Segments>
      </mssgle:Curve>
    </EdgeLayout.Curve>
    <EdgeLayout.Labels>
      <EdgeLabelCollection />
    </EdgeLayout.Labels>
  </EdgeLayout>
  <EdgeLayout
    Id="Package\\Load_Fact_Orders.Paths[Customer Match Output]"
    TopLeft="320,152">
    <EdgeLayout.Curve>
      <mssgle:Curve
        StartConnector="{assembly:Null}"
        EndConnector="0,38"
        Start="0,0"
        End="0,30.5">
        <mssgle:Curve.Segments>
          <mssgle:SegmentCollection
            Capacity="5">
            <mssgle:LineSegment
              End="0,30.5" />
          </mssgle:SegmentCollection>
        </mssgle:Curve.Segments>
      </mssgle:Curve>
    </EdgeLayout.Curve>
    <EdgeLayout.Labels>
      <EdgeLabelCollection />
    </EdgeLayout.Labels>
  </EdgeLayout>
  <EdgeLayout
    Id="Package\\Load_Fact_Orders.Paths[Product Match Output]"
    TopLeft="320,232">
    <EdgeLayout.Curve>
      <mssgle:Curve
        StartConnector="{assembly:Null}"
        EndConnector="0,38"
        Start="0,0"
        End="0,30.5">
        <mssgle:Curve.Segments>
          <mssgle:SegmentCollection
            Capacity="5">
            <mssgle:LineSegment
              End="0,30.5" />
          </mssgle:SegmentCollection>
        </mssgle:Curve.Segments>
      </mssgle:Curve>
    </EdgeLayout.Curve>
    <EdgeLayout.Labels>
      <EdgeLabelCollection />
    </EdgeLayout.Labels>
  </EdgeLayout>
  <EdgeLayout
    Id="Package\\Load_Fact_Orders.Paths[Seller Match Output]"
    TopLeft="320,312">
    <EdgeLayout.Curve>
      <mssgle:Curve
        StartConnector="{assembly:Null}"
        EndConnector="0,38"
        Start="0,0"
        End="0,30.5">
        <mssgle:Curve.Segments>
          <mssgle:SegmentCollection
            Capacity="5">
            <mssgle:LineSegment
              End="0,30.5" />
          </mssgle:SegmentCollection>
        </mssgle:Curve.Segments>
      </mssgle:Curve>
    </EdgeLayout.Curve>
    <EdgeLayout.Labels>
      <EdgeLabelCollection />
    </EdgeLayout.Labels>
  </EdgeLayout>
</GraphLayout>
]]></DTS:DesignTimeProperties>
</DTS:Executable>
'''

with open(out_path, "w", encoding="utf-8") as f:
    f.write(package_xml)

print(f"Full Visual Studio SSIS package generated at: {out_path}")

