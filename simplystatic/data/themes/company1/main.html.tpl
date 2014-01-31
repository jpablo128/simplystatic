
<html>

    <head>
        <meta charset="UTF-8">
        <title>${pageTitle}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
        <link rel="stylesheet" href="${themePath}style.css" type="text/css" media="screen,print" />
        <link rel="stylesheet" href="/font-awesome/css/font-awesome.css" type="text/css" media="screen,print" />
    </head>

    <body>
        <header>
            <div class="title-band">
                <div class="site-title">
                    <h1><a href="/">My Company</a></h1>
                </div>
                
                <div class="site-image">
                    <a class="site-image" href="/">home</a> 
                </div>
            </div>
            <div class="navbar">
                <nav class="main-nav">
                    <a href="/" title="Home"><i class="icon-home icon-2x"></i>  </a>
                    <a href="/services" title="Services">Services</a>
                    <a href="/locations" title="Locations">Locations</a>
                    <a href="/about" title="About">About</a>
                    <a href="/contact" title="Contact">Contact</a>
                </nav>
                <nav class="social-nav">
                    <a href="#" title="Twitter"><i class="icon-twitter-sign icon-2x"></i></a>
                    <a href="#" title="Facebook"><i class="icon-facebook-sign icon-2x"></i></a>
                </nav>
            </div>
        </header>

         <div class="content">
            <article class="page-content">
                ${pageContent}
            </article>

        </div>


        <footer id="footer" class="inner">
            <p>~ Copyright &copy; 2013 - My Company -
            <span class="credit">Powered by <a href="#"><strong>SimplyStatic</strong></a></span> ~</p>
        </footer>

    <body>

</html> 