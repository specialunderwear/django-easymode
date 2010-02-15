<?xml version="1.0"?>
<!-- 
      gettext.xslt
      
      Created by l.kerkhof on 2009-08-17.
      
      Adds getext markers to string serialized from db.
 -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
	<xsl:output encoding="UTF-8" indent="no" method="xml"/>
	<xsl:preserve-space  elements="*"/>

	<!-- add more types to the or if you want more types -->
	<!-- to be recorded to in catalog -->
	<xsl:template match="field[@type='CharField' or @type='URLField' or @type='TextField']">
		<field>
			<xsl:copy-of select="@*"/>
			<xsl:choose>
				<xsl:when test="text()">{% blocktrans %}<xsl:value-of select="."/>{% endblocktrans %}</xsl:when>
				<xsl:when test="richtext/node()">{% blocktrans %}<xsl:copy-of select="richtext/node()"/>{% endblocktrans %}</xsl:when>
			</xsl:choose>
		</field>
	</xsl:template>

	<!-- copy all nodes and attributes that don't need special care -->
	<xsl:template match="@*|node()">
		<xsl:copy>
			<xsl:apply-templates select="@*|node()"/>
		</xsl:copy>			
	</xsl:template>

</xsl:stylesheet>
