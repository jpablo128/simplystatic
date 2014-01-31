
<html>

    <head>
        <meta charset="UTF-8">
        <title>${pageTitle}</title>

        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
        <link rel="stylesheet" href="${themePath}style.css" type="text/css" media="screen,print" />
        <link rel="stylesheet" href="${themePath}pygments_default.css" type="text/css" media="screen,print" />
        <link rel="stylesheet" href="/font-awesome/css/font-awesome.css" type="text/css" media="screen,print" />
    </head>

    <body>
        <header>
            <div class="title-band">
                <div class="site-title">
                    <h1><a href="/">My Blog</a></h1>
                </div>
                <div class="site-byline">
                    <h2><a href="/">A blog about something</a></h2>
                </div>
                <div class="site-image">
                    <a class="site-image" href="/">home</a> 
                </div>
            </div>
            <div class="navbar">
                <nav class="main-nav">
                    <a href="/" title="Home"><i class="icon-home icon-2x"></i>  </a>
                    <a href="#" title="About"><i class="icon-info-sign icon-2x"></i></a>
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


        % if (not isFrontPage):
            <nav class="article-nav">
                <a class="back" href="javascript: history.go(-1)" title="Go Back"><i class="icon-arrow-left"></i></a>
            </nav>
        % endif


        <footer id="footer" class="inner">
            <p>~ Copyright &copy; 2013 - John Doe -
            <span class="credit">Powered by <a href="#"><strong>SimplyStatic</strong></a></span> ~</p>
        </footer>

    <body>

</html> 