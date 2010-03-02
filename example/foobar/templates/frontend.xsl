<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
	<xsl:output method="html" encoding="UTF-8" media-type="text/html"/>
	
	<!-- Render an object node -->
	<xsl:template match="object">
		<xsl:element name="{substring-after(@model,'.')}">
			<ul>
			<xsl:apply-templates select="field"/>
			</ul>
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
			<xsl:element name="li">
				<xsl:value-of select="."/>
			</xsl:element>
		</xsl:if>
	</xsl:template>
	
	<!-- Parse the root node of the serialized xml -->
	<xsl:template match="django-objects">
		<html>
			<head>
				<title>Fronttend</title>
			</head>
			<body>
				<p>Below you will see the same content as flash will load, only rendered as html.</p>
				
				<p>this example shows all the content flash loads from the /frontend/data.xml, but
					ideally you don't want to show all content at once. You should spread the content out
				over different pages. Put the same content on each page as you would have on a page
				in the flash movie eg:</p>
				
				<h4>flash url: /frontend/#/subpage (&lt;-- will load /frontend/data.xml)<br/></h4>
				<p>
					/frontend/ and /frontend/#subpage is the same url for google. the seo content of /frontend/ should
					only contain the data that the index page of you flash movie displays. All internal links in the flash
					movie should be links where the # is stripped. This way google will follow the links and it will find
					the content that belongs to these pages.
				</p>
				
				<h4>seo url:   /frontend/subpage (&lt;-- will also load /frontend/data.xml but move the flash movie to page #/subpage)</h4>
				<p>
					The page /frontend/subpage is different for google from /frontend/#subpage. This page should contain the content that is displayed
					on /frontend/#subpage in the flash movie. Google will never ever visit /frontend/#subpage because it is the same as /frontend/. Never
					ever leave any internal links containing # in the seo content!
				</p>
				<h3>Here is the seo content</h3>
				<xsl:apply-templates/>
			</body>
		</html>
	</xsl:template>
</xsl:stylesheet>
