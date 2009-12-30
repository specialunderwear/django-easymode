<?xml version="1.0" encoding="UTF-8"?>
<!-- 
    model-to-xml.xsl
    vacansoleil

    Created by l.kerkhof on 2009-07-30.
    Copyright 2009 LUKKIEN. All rights reserved.
-->
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output encoding="UTF-8" indent="yes" method="xml" />

    <xsl:template name="object-renderer">
        <xsl:element name="{substring-after(@model,'.')}">
            <xsl:for-each select="field">
                <xsl:if test="@type">
                    <xsl:element name="{@name}">
                            <xsl:attribute name="type">
                                <xsl:value-of select="@type"/>
                            </xsl:attribute>                                     
                        <xsl:value-of select="."/>
                    </xsl:element>
                </xsl:if>
            </xsl:for-each>
            <xsl:if test="object">
                <children>
                    <xsl:for-each select="object">
                            <xsl:call-template name="object-renderer"/>
                    </xsl:for-each>                                                
                </children>
            </xsl:if>

        </xsl:element>
    </xsl:template>

    <xsl:template match="django-objects">
        <xsl:for-each select="object">
            <xsl:call-template name="object-renderer"/>
        </xsl:for-each>
    </xsl:template>

</xsl:stylesheet>