package com.scbots.pagemaster;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.util.Log;
import android.view.GestureDetector;
import android.view.KeyEvent;
import android.view.MotionEvent;
import android.view.ViewConfiguration;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class PageMasterActivity extends Activity {
	String author;
	String illustrator;
	String startPage;
	
	/** Called when the activity is first created. */
	
	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.main);
		
		final WebView web = ((WebView)findViewById(R.id.webview));//new WebView(this);
		web.setWebViewClient(new WebViewClient(){
		    @Override
		    public boolean shouldOverrideUrlLoading(WebView view, String url)
		    {
		    	Log.e("url", url);
		    	if (url.contains("etsy")) {
		    		//Pass it to the system, doesn't match your domain
		            Intent intent = new Intent(Intent.ACTION_VIEW);
		            intent.setData(Uri.parse(url));
		            startActivity(intent);
		            //Tell the WebView you took care of it.
		            return true;
		    	}

		    	view.loadUrl(url);
		    	return false;
		    }
		});
		
		
		//web.setOnTouchListener(l)
        final GestureDetector gestureDetector = new GestureDetector(web.getContext(), new GestureDetector.SimpleOnGestureListener() {
            @Override
            public boolean onFling(MotionEvent e1, MotionEvent e2, float velocityX, float velocityY) {
            	final ViewConfiguration vc = ViewConfiguration.get(web.getContext());
            	final int SWIPE_MIN_DISTANCE = vc.getScaledTouchSlop();
            	final int SWIPE_THRESHOLD_VELOCITY = vc.getScaledMinimumFlingVelocity();
            	final int SWIPE_MAX_OFF_PATH = SWIPE_MIN_DISTANCE;
            	
                try {	
                    if (Math.abs(e1.getY() - e2.getY()) > SWIPE_MAX_OFF_PATH)
                    	return false;
                    
                    // right to left swipe
                    if(e1.getX() - e2.getX() > SWIPE_MIN_DISTANCE && Math.abs(velocityX) > SWIPE_THRESHOLD_VELOCITY) {
                    	if (web.canGoForward())
                    		web.goForward();
                    }  else if (e2.getX() - e1.getX() > SWIPE_MIN_DISTANCE && Math.abs(velocityX) > SWIPE_THRESHOLD_VELOCITY) {
                    	if (web.canGoBack())
                    		web.goBack();
                    }
                } catch (Exception e) {
                    // nothing
                }
                return false;
            }
        });
        /*
        web.setOnTouchListener(new View.OnTouchListener() {
            public boolean onTouch(View v, MotionEvent event) {
                return gestureDetector.onTouchEvent(event);
            }
        });
        */
		
		if (savedInstanceState != null)
			web.restoreState(savedInstanceState);
		else
			web.loadUrl("file:///android_asset/pagemaster_splash.html");
	}


	@Override
	public boolean onKeyDown(int keyCode, KeyEvent event) {
		WebView web = (WebView)findViewById(R.id.webview);
	    if ((keyCode == KeyEvent.KEYCODE_BACK) && web.canGoBack()) {
	        web.goBack();
	        return true;
	    }
	    return super.onKeyDown(keyCode, event);
	}
	
	protected void onSaveInstanceState(Bundle outState) {
		((WebView)findViewById(R.id.webview)).saveState(outState);
	}
	
}
