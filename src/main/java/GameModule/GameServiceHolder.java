package GameModule;

/**
* GameModule/GameServiceHolder.java .
* Generated by the IDL-to-Java compiler (portable), version "3.2"
* from GameService.idl
* Saturday, May 24, 2025 4:33:59 AM SGT
*/

public final class GameServiceHolder implements org.omg.CORBA.portable.Streamable
{
  public GameModule.GameService value = null;

  public GameServiceHolder ()
  {
  }

  public GameServiceHolder (GameModule.GameService initialValue)
  {
    value = initialValue;
  }

  public void _read (org.omg.CORBA.portable.InputStream i)
  {
    value = GameModule.GameServiceHelper.read (i);
  }

  public void _write (org.omg.CORBA.portable.OutputStream o)
  {
    GameModule.GameServiceHelper.write (o, value);
  }

  public org.omg.CORBA.TypeCode _type ()
  {
    return GameModule.GameServiceHelper.type ();
  }

}
