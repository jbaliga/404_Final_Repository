using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class distance : MonoBehaviour
{
    public Transform t1;
    public Transform t2;
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        //Vector3 direction = (t2-t1).normalized;
        //float angle =  Vector3.Angle(direction, unit.transform.forward);
        print("Distance: " + (Vector3.Distance(t1.position,t2.position)));
        //print("Angle: " + (Vector3.Angle(t1.position, t2.position)));
    }
}
