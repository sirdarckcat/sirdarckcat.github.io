<?xml version="1.0"?>

<xsl:stylesheet version="1.0" 
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		xmlns="http://www.w3.org/2000/svg"
		>
  <xsl:output
      method="xml"
      indent="yes"
      standalone="no"
      doctype-public="-//W3C//DTD SVG 1.1//EN"
      doctype-system="http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd"
      media-type="image/svg" />
  
  <xsl:template match="thing">
    <svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" >
      <rect x="10" y="10" width="{width}" 
	    height="{height}" fill="red" stroke="black"/>  
    </svg>
  </xsl:template>
</xsl:stylesheet>
