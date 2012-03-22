package com.scbots.pagemaster;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Paint.Style;
import android.graphics.Rect;
import android.os.Handler;
import android.util.Log;
import android.view.View;

public class PageView extends View {
	private Bitmap[] images;
	private int delay;
	private long startTime;
	final Handler handler = new Handler();
	
	final Runnable updateAnimation = new Runnable() {
        public void run() {
        	PageView.this.invalidate();
        	/*
            if (mTmpBitmap != null && !mTmpBitmap.isRecycled()) {
                GifDecoderView.this.setImageBitmap(mTmpBitmap);
            }
            */
        }
    };
	
	public PageView(Context context, Bitmap[] images, int delay) {
        super(context);
        this.images = images;
        this.delay = delay;
        this.startTime = 0;
        
        new Thread(new AnimatedRunnable(delay)).start();
    }
    
    @Override
    public void onDraw(Canvas canvas) {
    	super.onDraw(canvas);
    	
    	if (startTime == 0) {
    		startTime = System.currentTimeMillis();
    	}
    	final long elapsed = System.currentTimeMillis() - startTime;  
    	
    	// draw background
    	//
    	Paint paint = new Paint(); 
    	paint.setColor(Color.DKGRAY); 
    	paint.setStyle(Style.FILL); 
    	canvas.drawPaint(paint); 

    	//paint.setColor(Color.BLACK); 
    	//paint.setTextSize(20); 
    	//canvas.drawText("Some Text", 10, 25, paint); 
    	
    	//Log.i("foo", "" + (int)(elapsed / delay) % images.length);
    	// draw current bitmap
    	//
    	final Bitmap image = images[(int)(elapsed / delay) % images.length];
    	float aspect = (float)image.getWidth() / image.getHeight();
    	final int scaledHeight = (int)(image.getHeight() * ((float)this.getWidth() / image.getWidth()));
    	final int topMargin = (int)((this.getHeight() - scaledHeight) * 0.5f);
    	//final int bottomMargin = image.getHeight() + topMargin;
    	//Log.i("foo", "" + topMargin + " & " + scaledHeight);
    	canvas.drawBitmap(image, null, new Rect(0, topMargin, this.getWidth()-1, topMargin+scaledHeight), paint);
    }
    
    class AnimatedRunnable implements Runnable
    {
    	final int delay;
    	public AnimatedRunnable(int delay)
    	{
    		this.delay = delay;
    	}
    	
    	public void run() {
        	while (true) {
                handler.post(updateAnimation);
                try {
                   Thread.sleep(delay);
                } catch (InterruptedException e) {
                   e.printStackTrace();
                }
        	}
       }
    }
}
