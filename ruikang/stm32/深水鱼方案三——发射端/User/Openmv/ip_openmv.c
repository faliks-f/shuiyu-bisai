#include "ip_openmv.h"
#include "con_gear.h"
#include "bsp_usart.h"

uint8_t receive_array[Array_Length] = { 0xFF , 0xFF , 0xFF };//临时存储函数
uint8_t receive_length = 0;//当前存储位置
uint8_t receive_valid = 0;//当前存储状态

extern uint32_t watchdog_delay;
//协议定义区
uint8_t rudder_rotate_move[Array_Length]						= { 0x7A , 0xA1 , 0x85 };				//舵机前进转码
uint8_t rudder_rotate_stop[Array_Length]						= { 0x7A , 0xA2 , 0x85 };				//舵机停止转码
uint8_t rudder_rotate_left4[Array_Length]						= { 0x7A , 0xC2 , 0x85 };				//舵机右转码4
uint8_t rudder_rotate_right4[Array_Length]					= { 0x7A , 0xC1 , 0x85 };				//舵机左转码4
uint8_t rudder_rotate_left1[Array_Length]						= { 0x7A , 0xB2 , 0x85 };				//舵机右转码1
uint8_t rudder_rotate_right1[Array_Length]					= { 0x7A , 0xB1 , 0x85 };				//舵机左转码1
uint8_t point_find[Array_Length]										=	{ 0x7A , 0xD1 , 0x85 };				//检测漏点
extern uint8_t self_check_command[Array_Length];																		//查询上位机

void Decode(void)
{
	if(Array_Comparation(receive_array , rudder_rotate_move)){Gear_Control(1);Usart_SendArray(USART2,receive_array,Array_Length);}
	else if(Array_Comparation(receive_array , rudder_rotate_stop)){Gear_Control(0);Usart_SendArray(USART2,receive_array,Array_Length);}
	else if(Array_Comparation(receive_array , rudder_rotate_left4)){Gear_Control(2);Usart_SendArray(USART2,receive_array,Array_Length);}
	else if(Array_Comparation(receive_array , rudder_rotate_left1)){Gear_Control(3);Usart_SendArray(USART2,receive_array,Array_Length);}
	else if(Array_Comparation(receive_array , rudder_rotate_right1)){Gear_Control(4);Usart_SendArray(USART2,receive_array,Array_Length);}
	else if(Array_Comparation(receive_array , rudder_rotate_right4)){Gear_Control(5);Usart_SendArray(USART2,receive_array,Array_Length);}
	//else if(Array_Comparation(receive_array , point_find)){Usart_SendArray(USART2,point_find,Array_Length);}
	else if(Array_Comparation(receive_array , self_check_command)){Usart_SendArray(USART2,self_check_command,Array_Length);}
	else
	{
		if(receive_array[1] < 64) Usart_SendArray(USART2,receive_array,Array_Length);
	}
	watchdog_delay = 0;
	receive_array[0] = 0xFF;
	receive_array[1] = 0xFF;
	receive_array[2] = 0xFF;
}

void USART1_IRQHandler(void)
{
	if(USART_GetITStatus(DEBUG_USARTx, USART_IT_RXNE) == SET)
	{
		uint8_t receive = USART_ReceiveData(USART1);
		USART_ClearITPendingBit(USART1,USART_IT_RXNE);
		if(receive_valid == 1)//是否许可接收
		{
			receive_array[receive_length] = receive;
			receive_length++;
			if(Array_Length == receive_length)
			{
				Decode();
				receive_valid = 0;
				receive_length = 0;
			}
		}
		else 
		{
			if(receive == 0x7A)
			{
				receive_valid = 1;
				receive_length = 1;
				receive_array[0] = 0x7A;
			}
		}
	}
}

/*********************************************END OF FILE**********************/
