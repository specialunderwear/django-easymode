<?xml version="1.0"?>
<!-- 
	model-to-xml.xsl

	Created by l.kerkhof on 2009-07-30.
-->
<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:output encoding="UTF-8" indent="yes" method="xml" />

	<!-- Render an object node -->
	<xsl:template match="object">
		<xsl:element name="{substring-after(@model,'.')}">
			<xsl:apply-templates select="field"/>
			<xsl:if test="object">
				<children>
					<xsl:apply-templates select="object"/>
				</children>
			</xsl:if>

		</xsl:element>
	</xsl:template>

	<!-- render a field node -->
	<xsl:template match="field">
		<xsl:if test="@type">
			<xsl:element name="{@name}">
				<xsl:copy-of select="@type"/>
				<xsl:copy-of select="@font"/>
				<xsl:value-of select="."/>
			</xsl:element>
		</xsl:if>
	</xsl:template>

	<!-- just copy unmatched nodes -->
	<!-- so we know something is wrong -->
	<xsl:template match="@*|node()">
		<xsl:copy>
			<xsl:apply-templates select="@*|node()"/>
		</xsl:copy>
	</xsl:template>

	<!-- Parse the root node of the serialized xml -->
	<xsl:template match="django-objects">
		<root>
			<xsl:apply-templates/>
		</root>
	</xsl:template>

</xsl:stylesheet>
