<?xml version="1.0" encoding="UTF-8"?>
<!-- 
      gettext.xslt
      vacansoleil
      
      Created by l.kerkhof on 2009-08-17.
      Copyright 2009 LUKKIEN. All rights reserved.
      
      Adds getext markers to string serialized from db.
 -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <xsl:output encoding="UTF-8" indent="no" method="xml"/>
    <xsl:preserve-space  elements="*"/>
    <xsl:template match="django-objects">
        <django-objects version="1.0">
            <xsl:for-each select="object">
                <object>
                    <xsl:for-each select="@*">
                        <xsl:attribute name="{name()}">
                            <xsl:value-of select="."/>
                        </xsl:attribute>
                    </xsl:for-each>
                    <xsl:for-each select="field">
                        <xsl:choose>
                            <xsl:when test="@type = 'CharField'">
                                <field>
                                    <xsl:attribute name="type">
                                        <xsl:value-of select="@type"/>
                                    </xsl:attribute>
                                    <xsl:attribute name="name">
                                        <xsl:value-of select="@name"/>
                                    </xsl:attribute>
                                    <xsl:if test="text()">
                                        {% blocktrans %}<xsl:value-of select="."/>{% endblocktrans %}
                                    </xsl:if>
                                </field>
                            </xsl:when>
                            <xsl:when test="@type = 'TextField'">
                                <field>
                                    <xsl:attribute name="type">
                                        <xsl:value-of select="@type"/>
                                    </xsl:attribute>
                                    <xsl:attribute name="name">
                                        <xsl:value-of select="@name"/>
                                    </xsl:attribute>
                                    <xsl:choose>
                                        <xsl:when test="text()">
                                            {% blocktrans %}<xsl:value-of select="."/>{% endblocktrans %}
                                        </xsl:when>
                                        <xsl:when test="richtext/node()">
                                            {% blocktrans %}<xsl:copy-of select="richtext/node()"/>{% endblocktrans %}
                                        </xsl:when>
                                    </xsl:choose>
                                </field>
                            </xsl:when>							
                            <xsl:otherwise>
                                <xsl:copy-of select="."/>
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:for-each>
                </object>
            </xsl:for-each>
        </django-objects>
    </xsl:template>
</xsl:stylesheet>
