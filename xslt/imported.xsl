<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns="http://www.w3.org/1999/xhtml">

<xsl:template match="/root">
	<div class="default">Doesn't work.</div>
</xsl:template>

<xsl:template name="works">
	<div class="overridden">Works!</div>
</xsl:template>

</xsl:stylesheet>